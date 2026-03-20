from slowapi import Limiter
from fastapi import Request

def get_real_ip(request: Request):
    return request.headers.get("X-Forwarded-For", request.client.host if request.client else "127.0.0.1")

limiter = Limiter(key_func=get_real_ip)
