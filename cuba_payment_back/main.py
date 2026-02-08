"""Main FastAPI application"""

from fastapi import FastAPI

app = FastAPI(
    title="Cuba Payment API",
    description="Backend API for Cuba Payment application",
    version="0.1.0"
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Cuba Payment API"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
