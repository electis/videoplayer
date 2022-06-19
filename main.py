from os import listdir
from os.path import isdir, join, isfile

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

root = "/storage/download/learn/"

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
            files.append((filename, content))
    files = sorted(files)
    dirs = sorted([f for f in listdir(path) if isdir(join(path, f))])
    return dirs, files


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    dirs, files = get_content(root)
    return templates.TemplateResponse("index.html", {"request": request, "files": files, "dirs": dirs})


@app.get("/{name}", response_class=HTMLResponse)
async def subdir(request: Request, name: str):
    dirs, files = get_content(join(root, name))
    return templates.TemplateResponse("index.html", {"request": request, "files": files, "dirs": [], "name": name})
