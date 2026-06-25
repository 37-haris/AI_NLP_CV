from fastapi.templating import Jinja2Templates
from fastapi import Request

class PageService:
    def __init__(self):
        self.templates = Jinja2Templates(directory="template")

    def render_home(self, request: Request):
        template = self.templates.get_template("index.html")
        return template.render({"request": request})
    
    def render_landing(self, request:Request):
        template = self.templates.get_template("landing.html")
        return template.render({"request": request})