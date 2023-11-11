from src.session import session
from src.post import Post
from src.settings import *
import json

class User:
    def __init__(self, creatorId) -> None:
        self.creatorId = creatorId

        url = 'https://api.fanbox.cc/creator.get?creatorId={}'.format(self.creatorId)
        res = session.get(url)
        res.raise_for_status()
        self.name = res.json()['body']['user']['name']
        self.path = settings.download_dir.joinpath(self.name)
        self.data = None
        pass

    
    def __del__(self):
        usersdata = json.loads(settings.usersjson_dir.read_text('utf-8'))
        usersdata[self.creatorId] = self.data
        settings.usersjson_dir.write_text(json.dumps(usersdata, indent=4, allow_nan=True, ensure_ascii=False), 'utf-8')


    def _create(self): 
        usersdata = json.loads(settings.usersjson_dir.read_text('utf-8'))
        if self.creatorId not in usersdata:
            self.data = {
                'names': [
                    self.name
                ],
                'latest': '1970-01-01T00:00:00+00:00'
            }
            if self.path.exists() == False:
                self.path.mkdir()
        else:
            self.data = usersdata[self.creatorId]

        if self.name != self.data['names'][-1]:
            self.path.with_name(self.data['names'][-1]).rename(self.path.with_name(self.name))
            self.data['names'].append(self.name)
        

    def get_updates(self) -> list[Post]:
        from src import utility
        from datetime import datetime

        return utility.get_posts(
            self.creatorId, 
            datetime.strptime(self.data['latest'], utility.time_fmt)
        )
    

    def fetch_updates(self):
        self._create()
        from src.utility import download_posts
        
        latest = download_posts(self.get_updates(), self.path)
        if latest:
            self.data['latest'] = latest