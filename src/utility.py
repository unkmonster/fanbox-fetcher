def handle_title(full_text: str) -> str:
    import re
    url = re.compile(r'(https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]')
    at = re.compile(r'@\S+\s')
    tag = re.compile(r'#\S+\s')
    enter = re.compile(r'\r|\n\r?')
    nonsupport = re.compile(r'[/\\:*?"<>\|]')

    full_text = url.sub('', full_text)
    full_text = at.sub('', full_text)
    full_text = tag.sub('', full_text)
    full_text = enter.sub(' ', full_text)
    full_text = nonsupport.sub('', full_text)
    return full_text.strip()


from pathlib import Path
import re
from src.post import Post
from datetime import datetime


def norepeat(path) -> Path:
    path = Path(path)
    while path.exists():
        if path.stem[-1] == ')' and path.stem.rfind('(') != -1:
            l = path.stem.rfind('(')
            try:
                num = int(path.stem[l + 1:-1]) + 1
                path = path.with_stem(path.stem[:l] + F'({num})')
                continue
            except Exception as err:
                print(err)
        path = path.with_stem(path.stem + ' (1)')
    return path


def paginateCreator(creatorId) -> list[str]:
    """300 posts per url"""
    from urllib import parse
    from src.session import session

    url = 'https://api.fanbox.cc/post.paginateCreator?creatorId={}'.format(creatorId)
    res = session.get(url)
    body: list[str] = res.json()['body']
    
    result = []
    for i, u in enumerate(body):
        if not (i % 30):     
            result.append(re.sub('(?<=limit=)[0-9]+', '300', u))
    return result

time_fmt = '%Y-%m-%dT%H:%M:%S%z'

def get_posts(creatorId: str, limit: datetime = None):
    from src.session import session
    
    result = []
    for url in paginateCreator(creatorId):
        res = session.get(url)
        res.raise_for_status()

        for item in res.json()['body']['items']:
            if limit and datetime.strptime(item['publishedDatetime'], time_fmt) <= limit:
                break
            result.append(item['id'])
        

    return [Post.from_id(id) for id in result]


def download_posts(posts: list[Post], save_to: Path):
    from src import utility
    from src.session import session

    if not save_to.exists():
        save_to.mkdir()

    try:
        time = None
        for post in reversed(posts):
            target_noextension = save_to.joinpath(utility.handle_title(post.title))
            for url in post.urls:
                res = session.get(url)
                res.raise_for_status()

                # get suffix from url
                suffix = Path(url).suffix
                suffix = suffix[:suffix.rfind('?')] if suffix.rfind('?') != -1 else suffix
                
                np = utility.norepeat(str(target_noextension) + suffix)
                with open(np, 'wb') as f:
                    f.write(res.content)
                print(np)
            utility.norepeat(str(target_noextension) + '.txt').write_text(post.excerpt, 'utf-8')
            time = post.time
    finally:
        return time

        

