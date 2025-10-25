import asyncio
import sys
from pathlib import Path

current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from routers import auth_router, user_router, chat_router, events_router
from utils.start_utils import lifespan, run_app
from utils.global_error_handler import global_exception_handler
from exceptions import BaseAppException

app = FastAPI(
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(chat_router)
app.include_router(events_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# app.add_exception_handler(BaseAppException, global_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

@app.get("/")
async def root():
    return {"message": "BasedAgent API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "BasedAgent"}


if __name__ == '__main__':
    asyncio.run(run_app())
