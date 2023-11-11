import requests
import json
from dataclasses import dataclass
from pathlib import Path

import utility
# prev 实际是 next 不知道为啥网站里 prev 代表下一项

@dataclass
class Post:
    title: str
    excerpt: str
    urls: list[str]


@dataclass
class Node:
    post: Post
    prev: dict


download_dir = Path('download')

def init():
    global download_dir

    if not download_dir.exists():
        download_dir.mkdir()

    
def post_info(postid):
    url = 'https://api.fanbox.cc/post.info?postId={}'.format(postid)
    headers = {
        'origin': 'https://welkinovo.fanbox.cc'
    }
    res = requests.get(url, headers=headers)
    res.raise_for_status()

    body = res.json()['body']
    files = body['body']['files']

    title = body['title']
    excerpt = body['excerpt'] if 'excerpt' in body else ''
    urls = [f['url'] for f in files]
    return Node(
        Post(title, excerpt, urls), 
        body['prevPost']
    )


def get_all_post(head_id) -> list[Post]:
    head = post_info(head_id)
    result = [head.post]

    while head.prev:
        head = post_info(head.prev['id'])
        result.append(head.post)
    return result


def download_allpost(head_id):
    posts = get_all_post(head_id)

    for post in posts:
        title = utility.handle_title(post.title)
        for url in post.urls:
            res = requests.get(url)
            res.raise_for_status()
            
            suffix = Path(url).suffix
            suffix = suffix[:suffix.rfind('?')] if suffix.rfind('?') != -1 else suffix
            to_save = utility.norepeat(download_dir.joinpath(Path(title).with_suffix(suffix)))

            with open(to_save, 'wb') as f:
                f.write(res.content)
            print(to_save)
        utility.norepeat(download_dir.joinpath(Path(title).with_suffix('.txt'))).write_text(post.excerpt, 'utf-8')
