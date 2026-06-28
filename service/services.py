from datetime import datetime

from fastapi.templating import Jinja2Templates
from fastapi import Request
from schema.schema import RegisterRequest, LoginRequest
from fastapi import HTTPException
from repositories.user_repository import user_repository
import hashlib
import pytz


class PageService:
    def __init__(self):
        self.templates = Jinja2Templates(directory="template")

    def render_landing(self, request: Request):
        template = self.templates.get_template("index.html")
        return template.render({"request": request})
    
    def render_home(self, request:Request, user:dict):
        template = self.templates.get_template("landing.html")
        exp_timestamp = user.get("exp")
        france_tz = pytz.timezone("Europe/Paris")
        exp_formatted = (
            datetime.utcfromtimestamp(exp_timestamp)
            .replace(tzinfo=pytz.utc)
            .astimezone(france_tz)
            .strftime("%H:%M:%S")
        ) if exp_timestamp else "N/A"
        
        return template.render(
            request=request,
            username=user.get("firstname"),
            expires_at=exp_formatted
    )
    