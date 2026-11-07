from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse

from derivatives_risk_engine.api.routes_demo import router as demo_router
from derivatives_risk_engine.api.routes_pricing import router as pricing_router
from derivatives_risk_engine.api.routes_risk import router as risk_router


def create_app() -> FastAPI:
    """Create the FastAPI application."""
    # The API page carries the portfolio's favicon instead of FastAPI's.
    app = FastAPI(title="DeltaCore", docs_url=None)

    @app.get("/docs", include_in_schema=False)
    def docs() -> HTMLResponse:
        return get_swagger_ui_html(
            openapi_url=app.openapi_url or "/openapi.json",
            title="DeltaCore - Swagger UI",
            swagger_favicon_url="/demo-assets/favicon.svg",
        )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(pricing_router)
    app.include_router(risk_router)
    app.include_router(demo_router)
    return app


app = create_app()
