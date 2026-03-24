from fastapi import FastAPI
from blog_app.api.router import router as blog_router

app = FastAPI()

app.include_router(blog_router)
