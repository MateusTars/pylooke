import logging

from pathlib import Path
from typing import Optional

from subby import (
    CommonIssuesFixer, BilibiliJSONConverter, ISMTConverter,
    SAMIConverter, SMPTEConverter, WebVTTConverter, WVTTConverter
)

def convert(
    file: Path,
    out: Optional[Path] = None,
    language: Optional[str] = None,
    encoding: str = "utf-8",
    no_post_processing: bool = False,
    keep_short_gaps: bool = False
) -> bool:
    if not isinstance(file, Path):
        raise TypeError(f"Expected file to be a {Path} not {file!r}")
    if out and not isinstance(out, Path):
        raise TypeError(f"Expected out to be a {Path} not {out!r}")

    if not out:
        out = Path(file).with_suffix(".srt")

    logger = logging.getLogger("convert")

    data = file.read_bytes()
    converter = None

    if b"mdat" in data and b"moof" in data:
        if b"</tt>" in data:
            logger.info("Subtitle format: ISMT (DFXP in MP4)")
            converter = ISMTConverter()
        elif b"vttc" in data:
            logger.info("Subtitle format: WVTT (WebVTT in MP4)")
            converter = WVTTConverter()
    elif b"<SAMI>" in data:
        logger.info("Subtitle format: SAMI")
        converter = SAMIConverter()
    elif b"</tt>" in data or b"</tt:tt>" in data:
        logger.info("Subtitle format: DFXP/TTML/TTML2")
        converter = SMPTEConverter()
    elif b"WEBVTT" in data:
        logger.info("Subtitle format: WebVTT")
        converter = WebVTTConverter()
    elif data.startswith(b'{') and b'"Stroke"' in data and b'"background_color"' in data:
        logger.info("Subtitle format: JSON (Bilibili)")
        converter = BilibiliJSONConverter()

    if not converter:
        logger.error("Subtitle format was unrecognized...")
        return False

    srt = converter.from_bytes(data)
    logger.info("Converted subtitle to SubRip (SRT)")

    if not no_post_processing:
        processor = CommonIssuesFixer()
        processor.remove_gaps = not keep_short_gaps
        srt, status = processor.from_srt(srt, language=language)
        logger.info(f"Processed subtitle {['but no issues were found...', 'and repaired some issues!'][status]}")

    srt.save(out, encoding=encoding)
    logger.info(f"Saved to: {out}")
    logger.debug(f"Used character encoding {encoding}")

    return True