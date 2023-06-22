from pathlib import Path

from yt_dlp import YoutubeDL

import settings
import utils


def download():
    ydl_opts = {
        'format': 'best[height<=480]+best[ext=mp4]+bestaudio',
        'keepvideo': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }]
    }
    root_path = Path(settings.root)
    for cur_path in root_path.rglob("*"):
        if cur_path.is_dir() or not cur_path.suffix == '.url':
            continue
        url = cur_path.read_text('utf-8-sig')
        if not utils.youtube_get_id(url):
            continue
        print(cur_path)
        ydl_opts['outtmpl'] = str(cur_path.with_suffix('.mp4'))
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        cur_path.rename(cur_path.with_suffix(settings.bak_ext))


if __name__ == "__main__":
    download()
