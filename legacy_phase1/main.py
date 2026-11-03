from fastapi import FastAPI

from api.v1.api import api_router


app = FastAPI(
    title="API Oficina Mecânica",
    version="1.0.0"
)


app.include_router(
    api_router,
    prefix="/api/v1"
)


@app.get("/")
async def root():

    return {
        "message": "API Oficina Mecânica",
        "version": "1.0.0"
    }


# ==========================================================
# EXECUÇÃO LOCAL
# ==========================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True
    )
