from fastapi import FastAPI

from api.route import ocrservice

app = FastAPI(title="Ocr Service")

app.include_router(ocrservice.routes, prefix="/api/ocr", tags=["ocr"])


