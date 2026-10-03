from fastapi import FastAPI
from app.api.v1.endpoints import laptime, degredation, overtake, strategy, grid
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="F1 Analytics Dashboard API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(laptime.router, prefix="/api/v1", tags=["laptime"])
app.include_router(grid.router, prefix="/api/v1", tags=["grid"])
app.include_router(degredation.router, prefix="/api/v1", tags=["degradation"])
app.include_router(overtake.router, prefix="/api/v1", tags=["overtake"])
app.include_router(strategy.router, prefix="/api/v1", tags=["strategy"])


@app.get("/health")
def health_check():
    return {"status": "ok"}