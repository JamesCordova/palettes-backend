from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.presentation.error_handlers import register_error_handlers
from app.presentation.routers import (
    auth_router,
    colors_router,
    favorites_router,
    palettes_router,
    tags_router,
    users_router,
)

app = FastAPI(title="Palette Backend")

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_error_handlers(app)

app.include_router(auth_router.router)
app.include_router(users_router.router)
app.include_router(palettes_router.router)
app.include_router(colors_router.router)
app.include_router(favorites_router.router)
app.include_router(tags_router.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
