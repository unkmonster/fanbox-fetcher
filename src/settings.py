from dataclasses import dataclass
from pathlib import Path
import json


@dataclass
class Settings:
    root_dir = Path(R'F:\0x0\fanbox')
    download_dir = root_dir.joinpath('download')
    usersjson_dir = root_dir.joinpath('users.json')

settings = Settings() 

if not settings.download_dir.exists():
    settings.download_dir.mkdir(parents=True)
if not settings.usersjson_dir.exists():
    settings.usersjson_dir.write_text(json.dumps(dict()))