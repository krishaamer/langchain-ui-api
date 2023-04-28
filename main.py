from fastapi import FastAPI

from routers import router


app = FastAPI(
    title="LangChain UI backend",
    description="The backend for LangChain UI",
    version="0.0.1"
)

app.include_router(router)