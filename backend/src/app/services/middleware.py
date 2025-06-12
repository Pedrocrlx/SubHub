from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt, JWTError
from app.services.auth import SECRET_KEY, ALGORITHM

class JWTMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/auth/protected"):
            print(f"[DEBUG] Path: {request.url.path}")
            auth_header = request.headers.get("Authorization")
            print(f"[DEBUG] Authorization header: {auth_header}")

            if not auth_header or not auth_header.startswith("Bearer "):
                raise HTTPException(status_code=401, detail="Missing or invalid token")
            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                print(f" [DEBUG] User in payload: {payload.get('sub')}")
                request.state.user = payload.get("sub")
            except JWTError:
                raise HTTPException(status_code=401, detail="Invalid token")
        return await call_next(request)
