from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from jose import jwt, JWTError
from service.services import PageService
from service.user_service import SECRET_KEY, ALGORITHM

router       = APIRouter(tags=["Pages"])
page_service = PageService()


def is_authenticated(request: Request) -> bool:
    token = request.cookies.get("access_token")
    if not token:
        return False
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return True
    except JWTError:
        return False

def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return None

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # contains username, email, etc.
    except JWTError:
        return None
    


@router.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    if is_authenticated(request):
        return RedirectResponse(url="/chat")
    return page_service.render_landing(request)


@router.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(url="/")
    user = get_current_user(request)
    html = page_service.render_home(request, user)
    response = HTMLResponse(content=html)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    return response


        


