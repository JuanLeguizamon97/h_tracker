from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
import logging

# Configurar el logger para registrar excepciones
logger = logging.getLogger("error_handler")
logger.setLevel(logging.ERROR)

class ErrorHandler(BaseHTTPMiddleware):

    def __init__(self, app: FastAPI) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next) -> Response:
        try:
            # Intentar procesar la solicitud
            return await call_next(request)
        except HTTPException as http_exc:
            # Si es una excepción HTTP, devolver la respuesta con el código adecuado
            return JSONResponse(status_code=http_exc.status_code, content={'error': http_exc.detail})
        except Exception as e:
            # Registrar el error y devolver un error 500 en caso de excepción general
            logger.error(f"Error en la solicitud: {str(e)}", exc_info=True)
            return JSONResponse(status_code=500, content={'error': 'Internal Server Error'})