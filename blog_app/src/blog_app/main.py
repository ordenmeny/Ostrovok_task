from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def hello_world():
    return {"response": "Hello, world!"}

