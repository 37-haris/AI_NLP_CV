from controller.Controller import router
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


app = FastAPI(title="Image Captioning with AI")

# I am using this for the reading my css and js
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(router)
