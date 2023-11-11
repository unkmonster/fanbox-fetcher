import sys
import os
sys.path.append(os.getcwd())
import json
from src.user import User
from src.settings import settings

with open(settings.usersjson_dir, encoding='utf-8') as f:
    j = json.load(f)

    for id in j:
        User(id).fetch_updates()