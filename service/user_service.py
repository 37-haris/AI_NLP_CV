import hashlib
from jose import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Response
from fastapi.responses import RedirectResponse
from schema.schema import RegisterRequest, LoginRequest
from repositories.user_repository import user_repository

SECRET_KEY = "db521a9981fcfd50f4327ff3680c9ec1b3c6f9c5f2338ef8527cd28398cf2410"
ALGORITHM  = "HS256"


def create_access_token(user: dict) -> str:
    expire  = datetime.utcnow() + timedelta(minutes=1)
    payload = {"sub": str(user["id"]),
               "firstname": user["firstname"],
               "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


class UserService:

    @staticmethod
    def _hash(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, data: RegisterRequest) -> dict:
        existing = user_repository.find_by_username(data.username.strip())
        if existing:
            raise HTTPException(
                status_code=409,
                detail="Ce nom d'utilisateur est déjà pris."
            )

        success = user_repository.create(
            username=data.username.strip(),
            firstname=data.firstname.strip(),
            lastname=data.lastname.strip(),
            hashed_password=self._hash(data.password)
        )

        if not success:
            raise HTTPException(
                status_code=500,
                detail="Erreur lors de la création du compte."
            )

        return {"message": "Compte créé avec succès."}

    def login(self, data: LoginRequest, response: Response) -> dict:
        user = user_repository.find_by_credentials(
            username=data.username.strip(),
            hashed_password=self._hash(data.password)
        )

        if not user:
            raise HTTPException(
                status_code=401,
                detail="Nom d'utilisateur ou mot de passe incorrect."
            )

        token = create_access_token(user)

        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            max_age=60
        )

        return {
            "access_token": token,
            "token_type":   "bearer",
            "user": {
                "id":        user["id"],
                "username":  user["username"],
                "firstname": user["firstname"],
                "lastname":  user["lastname"],
            }
        }

    def logout(self, response: Response) -> RedirectResponse:
        redirect = RedirectResponse(url="/", status_code=302)
        redirect.delete_cookie("access_token")
        return redirect


user_service = UserService()