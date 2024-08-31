"""
A browser-based UI for running the translation helper tool.
"""

import logging
import pathlib

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .commands import flush_to_localisation, reload_localisation_to_tsv
from .config_utils import Config, load_config, save_config

app = FastAPI()

this_dir = pathlib.Path(__file__).parent
app.mount("/static", StaticFiles(directory=this_dir / "static"), name="static")
templates = Jinja2Templates(directory=this_dir / "templates")


@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/config", response_class=HTMLResponse)
async def get_config(request: Request):
    config = load_config()
    return templates.TemplateResponse(request=request, name="config.html.j2", context={"config": config})


@app.post("/config", response_class=HTMLResponse)
async def post_config(request: Request):
    formdata = await request.form()
    config = Config(
        reference_directory=formdata["reference_directory"],
        reference_language=formdata["reference_language"],
        translation_filepath=formdata["translation_filepath"],
        translation_language=formdata["translation_language"],
    )
    save_config(config=config)
    return templates.TemplateResponse(request=request, name="config.html.j2", context={"config": config})


@app.post("/reload_localisations", response_class=HTMLResponse)
async def post_reload_localisation():
    config = load_config()
    try:
        info = reload_localisation_to_tsv(
            ref_dir=config.reference_directory,
            transl_fp=config.translation_filepath,
            reference_language=config.reference_language,
            translation_language=config.translation_language,
            reference_exclude_patterns=config.exclude_references,
        )
    except Exception as e:  # pylint: disable=broad-exception-caught
        content = f"""<p style="color: red;">{type(e).__name__}: {e}</p>"""
        logging.exception(e)
    else:
        content = f"""<p>{info}</p>"""
    return HTMLResponse(content=content)


@app.post("/flush_translations", response_class=HTMLResponse)
async def post_flush_translations():
    config = load_config()
    try:
        info = flush_to_localisation(
            transl_fp=config.translation_filepath,
            translation_language=config.translation_language,
        )
    except Exception as e:  # pylint: disable=broad-exception-caught
        content = f"""<p style="color: red;">{type(e).__name__}: {e}</p>"""
        logging.exception(e)
    else:
        content = f"""<p>{info}</p>"""
    return HTMLResponse(content=content)
