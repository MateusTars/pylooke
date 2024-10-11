# pylooke
Python library for interacting with [Looke](https://www.looke.com.br/) API.

# Installation
```
git clone https://github.com/MateusTars/pylooke
cd pylooke
pip install .
```

# Command line usage
```
Usage: pylooke [OPTIONS] COMMAND [ARGS]...

  Python library for interacting with Looke API.

Options:
  -d, --debug  Enable debug level logs.
  --help       Show this message and exit.

Commands:
  subrip   Download and process subtitles for the specified media ID.
  version  Print version.
```

# Subrip usage
```
Usage: pylooke subrip [OPTIONS] MEDIA_ID

  Download and process subtitles for the specified media ID.

Options:
  -l, --language TEXT       Specify the language code for the subtitles to
                            download (default: pt-BR).
  -o, --output-folder PATH  Specify the output folder to save subtitles
                            (default: Subtitles).
  -s, --season INTEGER      Specify the season number for which subtitles
                            should be downloaded.
  -a, --all-season          Download subtitles for all seasons instead of a
                            specific one. Overrides the --season option.
  -k, --keep                Keep the original subtitle file after download
                            (default: False).
  -c, --convert-to-srt      Convert the downloaded subtitles to SRT format
                            (default: True).
  --help                    Show this message and exit.
```

### Example
```
Movies:
    pylooke subrip https://www.looke.com.br/detalhes/421002
Series:
    pylooke subrip https://www.looke.com.br/detalhes/42868 --season 1
```

# Notes
**To get media details(find_media), authentication is not required; this includes subrip.**

# Library usage

```python
from pylooke.encripta.looke import Looke

if __name__ == "__main__":
    # For example, media ID for https://www.looke.com.br/detalhes/421002 is 421002.
    media_id = 421002 # int

    # Initialize the Looke client
    looke = Looke()

    # Get media details(Title, year, description, manifest, subtitles and etc)
    media_result = looke.find_media(media_id)

    # Login with username and password
    login_essentials_result = looke.login_essentials(
        username="example@email.com",
        password="example12345"
    )

    # Acquiring EME license response(bytes)
    challenge = b"" # EME license request(bytes)
    license_response = looke.get_license(
        challenge=challenge,
        media_id=media_id,
        user_id=login_essentials_result["User"]["UserId"],
        machine_id=login_essentials_result["MachineId"]
    )
```