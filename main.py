from os import listdir
from os.path import isdir, join, isfile

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import FileResponse

root = "/storage/download/learn/"
only_files = 'l.electis.ru'

app = FastAPI()
templates = Jinja2Templates(directory=".")


def get_content(path):
    files = []
    for filename in listdir(path):
        if isfile(join(path, filename)):
            content = filename
            if filename.endswith('.url'):
                with open(join(path, filename), encoding="utf-8-sig") as f:
                    content = f.readline()
            elif filename.endswith('.txt'):
                with open(join(path, filename), encoding="utf-8-sig") as f:
                    content = f.read()
            elif filename.endswith('.ico'):
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
    return templates.TemplateResponse("index.html", {"request": request, "files": files, "dirs": dirs})


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
        "name": name,
        "prev": prev,
        "path": '/'.join(path),
    })
