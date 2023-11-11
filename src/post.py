from src.session import session
from dataclasses import dataclass

@dataclass
class Post:
    title: str
    excerpt: str
    urls: list[str]
    time: str

    @classmethod
    def from_id(cls, postid):
        url = 'https://api.fanbox.cc/post.info?postId={}'.format(postid)
        res = session.get(url)
        res.raise_for_status()

        body = res.json()['body']
        files = body['body'].get('files')
        filemap: dict = body['body'].get('fileMap')

        title = body['title']
        excerpt = body['excerpt'] if 'excerpt' in body else ''
        urls = [f['url'] for f in files] if files else [item['url'] for item in filemap.values()] if files or filemap else []
        time = body['publishedDatetime']
        return cls(title, excerpt, urls, time)