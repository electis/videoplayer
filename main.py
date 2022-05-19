from glob import glob
from os import listdir
from os.path import isdir, join

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

root = "/storage/download/learn/"

app = FastAPI()
app.mount("/static", StaticFiles(directory=root))
templates = Jinja2Templates(directory=".")


def get_content(path):
    files = glob(join(path, "*.mp4"))
    dirs = [f for f in listdir(path) if isdir(join(path, f))]
    return dirs, files


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    dirs, files = get_content(root)
    return templates.TemplateResponse("index.html", {"request": request, "files": files, "dirs": dirs})


@app.get("/{name}", response_class=HTMLResponse)
async def subdir(request: Request, name: str):
    dirs, files = get_content(join(root, name))
    return templates.TemplateResponse("index.html", {"request": request, "files": files, "dirs": [], "name": name})
