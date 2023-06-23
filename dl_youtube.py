from pathlib import Path

from yt_dlp import YoutubeDL

import settings
import utils


def download():
    root_path = Path(settings.root)
    for cur_path in root_path.rglob("*"):
        if cur_path.is_dir() or not cur_path.suffix == '.url':
            continue
        url = cur_path.read_text('utf-8-sig')
        if not utils.youtube_get_id(url):
            continue
        print(cur_path)
        ydl_opts = {
            'format': f'best[height<720]+best[ext={settings.video_ext[1:]}],bestaudio[ext={settings.audio_ext[1:]}]',
            'outtmpl': cur_path.with_suffix('.%(ext)s').as_posix()
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        cur_path.rename(cur_path.with_suffix(settings.bak_ext))


if __name__ == "__main__":
    download()
