from pathlib import Path

from yt_dlp import YoutubeDL

import settings
import utils


def download(cur_path: Path, url, playlist=False):
    ydl_opts = dict(format=settings.download_format, ignoreerrors=True)

    if playlist:
        dir = cur_path.with_suffix('.pls')
        dir.mkdir(exist_ok=True)
        ydl_opts['outtmpl'] = dir.as_posix() + '/%(playlist_index)s. %(title)s.%(ext)s'
    else:
        ydl_opts['outtmpl'] = cur_path.with_suffix('.%(ext)s').as_posix()

    with YoutubeDL(ydl_opts) as ydl:
        result = ydl.download([url])

    if result == 0:
        cur_path.rename(cur_path.with_suffix(settings.bak_ext))


def main():
    root_path = Path(settings.root)

    for cur_path in root_path.rglob("*"):
        if cur_path.is_dir() or not cur_path.suffix == '.url':
            continue

        url = cur_path.read_text('utf-8-sig')
        print(cur_path, url)

        if utils.youtube_get_id(url):
            download(cur_path, url)
        elif 'youtube.com/playlist' in url:
            download(cur_path, url, playlist=True)


if __name__ == "__main__":
    main()
