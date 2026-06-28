from fastapi import APIRouter, File, Form, Request, Response, UploadFile
from fastapi.responses import JSONResponse
from jose import jwt, JWTError
import traceback
from AI_Model.Model_service import describe_image, translate_to_french
from schema.schema import RegisterRequest, LoginRequest, RegisterResponse
from service.user_service import user_service, SECRET_KEY, ALGORITHM
from service.chat_service import save_image

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_user_id(request: Request) -> int | None:
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return int(payload.get("sub"))
    except (JWTError, TypeError):
        return None


@router.post("/register", response_model=RegisterResponse, status_code=201)
def register(data: RegisterRequest):
    return user_service.register(data)


@router.post("/login")
def login(data: LoginRequest, response: Response):
    return user_service.login(data, response)


@router.get("/logout")
def logout(response: Response):
    return user_service.logout(response)


@router.post("/predict")
async def predict(
    request:   Request,
    image:     UploadFile = File(...),
    user_text: str        = Form(default=""),
):
    try:
        image_bytes    = await image.read()
        en_description = describe_image(image_bytes)

        if user_text.strip():
            en_description += f"  (Note: {user_text.strip()})"

        fr_description = translate_to_french(en_description)

        # Save image to disk
        user_id    = get_user_id(request)
        image_path = None
        if user_id:
            image_path = save_image(image_bytes, user_id, image.filename)

        return JSONResponse({
            "en":         en_description,
            "fr":         fr_description,
            "image_path": image_path
        })

    except Exception as exc:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(exc)})