from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Math AI Backend Running"}