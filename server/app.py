from fastapi import FastAPI

app = FastAPI()


@app.get("/opa")
def opa():
    return {"message": "opa"}
