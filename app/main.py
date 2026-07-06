from fastapi import FastAPI

from app.presentation.error_handlers import register_error_handlers
from app.presentation.routers import (
    colors_router,
    favorites_router,
    palettes_router,
    tags_router,
    users_router,
)

app = FastAPI(title="Palette Backend")

register_error_handlers(app)

app.include_router(users_router.router)
app.include_router(palettes_router.router)
app.include_router(colors_router.router)
app.include_router(favorites_router.router)
app.include_router(tags_router.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
