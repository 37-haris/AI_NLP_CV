from controller.page_controller import router
from controller.user_controller import router as auth_router
from controller.chat_controller import router as chat_router    
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from database.db import init_db


app = FastAPI(title="Image Captioning with AI", doc_url="/swagger", redoc_url="/redoc")
# Init DB on startup
@app.on_event("startup")
def startup():
    init_db()

# I am using this for the reading my css and js
app.mount("/documentation", StaticFiles(directory="site", html=True), name="documentation")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(router)
app.include_router(auth_router)
app.include_router(chat_router)
