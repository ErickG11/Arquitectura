from fastapi import FastAPI
from routes.report import report_router

app = FastAPI()

app.include_router(report_router, prefix="/report")  # O sin prefix si prefieres solo "/generate"
