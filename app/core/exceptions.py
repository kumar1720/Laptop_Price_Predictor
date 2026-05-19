from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

class ModelPredictionException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

def setup_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "detail": exc.detail, "error_code": "HTTP_ERROR"},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "detail": "Validation error in request parameters",
                "errors": exc.errors(),
                "error_code": "VALIDATION_ERROR"
            },
        )

    @app.exception_handler(ModelPredictionException)
    async def model_prediction_exception_handler(request: Request, exc: ModelPredictionException):
        return JSONResponse(
            status_code=500,
            content={"success": False, "detail": exc.message, "error_code": "MODEL_PREDICTION_ERROR"},
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"success": False, "detail": str(exc), "error_code": "INTERNAL_SERVER_ERROR"},
        )
