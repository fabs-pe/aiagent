from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from footseo_agent import FootSeoAgent

app = FastAPI()
agent = FootSeoAgent()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "result": None,
            "topic": ""
        }
    )


@app.post("/", response_class=HTMLResponse)
def generate(request: Request, topic: str = Form(...)):
    result = agent.generate_seo_draft(topic)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "result": result,
            "topic": topic
        }
    )