import re
import logging

from typing import Optional
from pathlib import Path
from datetime import datetime

from pathvalidate import sanitize_filename

import click

from pylooke import Looke, __version__
from pylooke.utils import subtitle

@click.group()
@click.option("-d", "--debug", is_flag=True, default=False, help="Enable debug level logs.")
def main(debug: bool):
    """Python library for interacting with Looke API."""
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)

@main.command()
def version():
    """Print version."""
    logger = logging.getLogger(__name__)

    copyright_years = 2024
    current_year = datetime.now().year
    if copyright_years != current_year:
        copyright_years = f"{copyright_years}-{current_year}"

    logger.info("pylooke version %s Copyright (c) %s MateusTars", __version__, copyright_years)
    logger.info("https://github.com/MateusTars/pylooke")

@main.command()
@click.argument("media_id", type=str)
@click.option(
    "-l",
    "--language",
    type=str,
    default="pt-BR",
    help="Specify the language code for the subtitles to download (default: pt-BR)."
)
@click.option(
    "-o",
    "--output-folder",
    type=Path,
    default="Subtitles",
    help="Specify the output folder to save subtitles (default: Subtitles)."
)
@click.option(
    "-s",
    "--season",
    type=int,
    default=None,
    help="Specify the season number for which subtitles should be downloaded."
)
@click.option(
    "-a",
    "--all-season",
    is_flag=True,
    default=False,
    help="Download subtitles for all seasons instead of a specific one. Overrides the --season option."
)
@click.option(
    "-k",
    "--keep",
    is_flag=True,
    default=False,
    help="Keep the original subtitle file after download (default: False)."
)
@click.option(
    "-c",
    "--convert-to-srt",
    is_flag=True,
    default=True,
    help="Convert the downloaded subtitles to SRT format (default: True)."
)
def subrip(
    media_id: str,
    language: str,
    output_folder: Path,
    season: Optional[int],
    all_season: bool,
    keep: bool,
    convert_to_srt: bool
):
    """
    Download and process subtitles for the specified media ID.
    """
    logger = logging.getLogger("subrip")

    if media_id[:4] == "http":
        media_id = media_id.split("/")[-1]

    if not media_id.isdigit():
        raise click.ClickException(f"Invalid media ID: '{media_id}'. It must be a numeric value.")

    media_id = int(media_id)

    logger.info(f"Starting subrip for media id: {media_id}")

    looke = Looke()

    data = looke.find_media(media_id)

    episodes = []
    if season or all_season:
        parent_id = data.get("ParentId")
        seasons_data = []
        if parent_id:
            seasons_data = looke.find_media(
                media_id=parent_id,
                groups={
                    "GroupName": "PlayDetails",
                    "GroupProperties": "LastPosition|Status"
                }
            )

        if parent_id and seasons_data and all(
            s["ParentId"] == parent_id
            for s in seasons_data["Childs"]
        ):
            for s in seasons_data["Childs"]:
                episodes.extend(
                    looke.find_media(media_id=s["Id"])["Childs"]
                )
        else:
            for episode in data.get("Childs", []):
                episodes.append(episode)

    medias = episodes or [data]

    for result in medias:
        subtitles = result["FileInfo"].get("Subtitles", [])

        full_title = result["FullTitle"]
        year = result["Metadata"].get("Year", 0)
        id_ = result["Id"]

        if not subtitles:
            logger.warning(f"No subtitle for {full_title} - {year} (ID: {id_}).")
            continue

        if result["SerieInfo"].get("Position"):
            season_number = re.search(r"(\d+)ª", full_title).group(1)
            if season != int(season_number) and not all_season:
                continue
            series_dir = Path(
                sanitize_filename(
                    filename=f"{full_title.split(' - ')[0].strip()} - S{season_number.zfill(2)}"
                )
            )
            folder = output_folder / series_dir
        else:
            folder = output_folder / Path(sanitize_filename(filename=f"{full_title} - {year}"))

        folder.mkdir(parents=True, exist_ok=True)

        logger.info(f"Downloading subtitle for {full_title} - {year} (ID: {id_}).")

        for subtitle_data in subtitles:
            if subtitle_data["Code"].lower() != language.lower():
                continue

            logger.info(
                f"Subtitle Name: {subtitle_data['Name']} - Language Code: {subtitle_data['Code']}"
            )

            subtitle_url = subtitle_data["UrlVTT"]

            filename = sanitize_filename(
                filename=f"{full_title} {year} {subtitle_data['Code']} {id_}.{subtitle_url.split('.')[-1]}"
            )

            file = folder / filename

            file.write_bytes(
                looke.send_request(
                    method="GET",
                    url=subtitle_url
                ).content
            )

            if convert_to_srt:
                status = subtitle.convert(
                    file=file
                )

                if not status:
                    raise click.ClickException("Subtitle conversion failed.")

            if not keep:
                file.unlink()

    logger.info("Finished.")


if __name__ == "__main__":
    main()