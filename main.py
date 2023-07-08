import pathlib
from os import remove
from os.path import join, isfile
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from natsort import natsorted
from starlette.responses import FileResponse, RedirectResponse
from moviepy.editor import AudioFileClip
from uvicorn import run

import settings
from settings import *

app = FastAPI()
templates = Jinja2Templates(directory=".")


def get_content(path):
    files = []
    path_ = Path(path)
    filenames: set[pathlib.Path] = {f for f in path_.glob("*") if f.is_file()}

    for filename in filenames:
        if filename.suffix == '.ico' or filename.suffix == bak_ext:
            continue
        content = filename.name
        if filename.suffix == '.url':
            content = filename.read_text("utf-8-sig")
        elif filename.suffix in ('.txt', settings.bak_ext):
            content = filename.read_text("utf-8-sig")
        elif filename.suffix == video_ext:
            audio = filename.with_suffix(audio_ext)
            content = audio.name if audio in filenames else False
        elif filename.suffix == audio_ext:
            if filename.with_suffix(video_ext) in filenames:
                continue
        files.append((filename.name, content))

    files = natsorted(files)
    dirs = natsorted([f.name for f in path_.glob("*") if f.is_dir()])
    return dirs, files


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    if request.base_url.hostname == only_files:
        raise HTTPException(status_code=404, detail="Wrong url")
    dirs, files = get_content(root)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "files": files,
        "dirs": dirs,
        "name": '',
        "path": '',
        "converting": isfile(converting_flag),
        "video_ext": video_ext,
    })


@app.get("/{name}", response_class=HTMLResponse)
async def subdir(request: Request, name: str):
    if name == 'favicon.ico':
        return FileResponse(f'{root}favicon.ico')
    path = name.split('@')
    try:
        dirs, files = get_content(join(root, *path))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Wrong url")
    prev = '/' + '@'.join(path[:-1])
    if request.base_url.hostname == only_files:
        dirs = []
        prev = None
    return templates.TemplateResponse("dir.html", {
        "request": request,
        "files": files,
        "dirs": dirs,
        "name": name + '@',
        "path": '/'.join(path) + '/',
        "prev": prev,
        "converting": isfile(converting_flag),
        "video_ext": video_ext,
    })


@app.post("/{name}", response_class=HTMLResponse)
async def convert(request: Request, name: str, background_tasks: BackgroundTasks):
    path = name.split('@')
    if DEBUG:
        converter(path)
    else:
        background_tasks.add_task(converter, path)
        flag = open(converting_flag, "w+")
        flag.close()
    return RedirectResponse('/' + '@'.join(path[:-1]), status_code=302)


def converter(path: list):
    audio = AudioFileClip(join(root, *path))
    audio.write_audiofile(join(root, *path[:-1], f'{path[-1][:-4]}{audio_ext}'), codec='aac')
    audio.close()
    if isfile(converting_flag):
        remove(converting_flag)


if __name__ == "__main__":
    run(app, host='0.0.0.0', port=9090)
