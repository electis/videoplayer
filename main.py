from os import listdir, remove
from os.path import isdir, join, isfile

from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import FileResponse, RedirectResponse
from moviepy.editor import AudioFileClip

DEBUG = 0

audio_ext = '.mp3'
root = "/storage/download/learn/"
only_files = 'l.electis.ru'
converting_flag = 'converting.tmp'

app = FastAPI()
templates = Jinja2Templates(directory=".")


def get_content(path):
    files = []
    filenames = {f for f in listdir(path) if isfile(join(path, f))}

    for filename in filenames:
        content = filename
        if filename.endswith('.url'):
            with open(join(path, filename), encoding="utf-8-sig") as f:
                content = f.readline()
        elif filename.endswith('.txt'):
            with open(join(path, filename), encoding="utf-8-sig") as f:
                content = f.read()
        elif filename.endswith('.ico'):
            continue
        elif filename.endswith('.mp4'):
            audio = f"{filename}{audio_ext}"
            content = audio if audio in filenames else False
        elif filename.endswith(audio_ext):
            if filename[:-4] in filenames:
                continue
        files.append((filename, content))

    files = sorted(files)
    dirs = sorted([f for f in listdir(path) if isdir(join(path, f))])
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
    audio.write_audiofile(join(root, *path[:-1], f'{path[-1]}{audio_ext}'))
    audio.close()
    if isfile(converting_flag):
        remove(converting_flag)
