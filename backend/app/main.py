from fastapi import FastAPI

app = FastAPI(
    title="AI Digital Twin",
    version="1.0.0",
)


@app.get("/")
async def root():
    return {"message": "AI Digital Twin API is running 🚀"}


@app.get("/health")
async def health():
    return {"status": "healthy"}