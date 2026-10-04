from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, HTMLResponse

router = APIRouter()
_STATIC = Path(__file__).with_name("static")


@router.get("/demo", response_class=HTMLResponse)
def demo() -> HTMLResponse:
    return HTMLResponse((_STATIC / "demo.html").read_text())


@router.get("/demo-assets/{name}", include_in_schema=False)
def asset(name: str) -> FileResponse:
    if name not in {"demo.css", "demo.js"}:
        raise HTTPException(status_code=404, detail="Asset not found")
    return FileResponse(_STATIC / name)
