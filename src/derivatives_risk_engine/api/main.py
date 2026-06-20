from fastapi import FastAPI

from derivatives_risk_engine.api.routes_pricing import router as pricing_router


def create_app() -> FastAPI:
    """Create the FastAPI application."""
    app = FastAPI(title="DeltaCore")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(pricing_router)
    return app


app = create_app()
