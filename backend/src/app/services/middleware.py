from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt, JWTError
from app.services.auth import SECRET_KEY, ALGORITHM

class JWTMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request.state.user = None  # To always initialise (Giulio)

        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                print(f"[DEBUG] User in payload: {payload.get('sub')}")
                request.state.user = payload.get("sub")
            except JWTError:
                print("[DEBUG] Invalid JWT")
                raise HTTPException(status_code=401, detail="Invalid token")

        return await call_next(request)