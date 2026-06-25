from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
import traceback

from service.services import PageService
from AI_Model.Model_service import describe_image, translate_to_french

router       = APIRouter()
page_service = PageService()


# ── Page routes ──────────────────────────────────────────────────────────────

@router.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    content = page_service.render_home(request=request)
    return HTMLResponse(content=content)


@router.get("/landing", response_class=HTMLResponse)
async def landing_page(request: Request):
    content = page_service.render_landing(request=request)
    return HTMLResponse(content=content)


# ── Prediction route ──────────────────────────────────────────────────────────

@router.post("/predict")
async def predict(
    image:     UploadFile = File(...),
    user_text: str        = Form(default=""),
):
    """
    Receives a multipart form with:
      - image     : the uploaded image file
      - user_text : optional extra note from the user

    Returns JSON: { "en": "...", "fr": "..." }
    """
    try:
        image_bytes = await image.read()

        # 1. English description from your model
        en_description = describe_image(image_bytes)

        # 2. Append user note if provided
        if user_text.strip():
            en_description += f"  (Note: {user_text.strip()})"

        # 3. French translation via Groq
        fr_description = translate_to_french(en_description)

        return JSONResponse({"en": en_description, "fr": fr_description})

    except Exception as exc:
        traceback.print_exc(),   # 👈 THIS IS CRITICAL
        # Return a clean error so the frontend can display it
        return JSONResponse(
            status_code=500,
            content={"error": str(exc)},
        )