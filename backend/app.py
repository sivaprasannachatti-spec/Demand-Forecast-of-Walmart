from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from backend.routes.forecast_route import router
from backend.services.forecast_service import get_formatted_forecast, _load_cache
import os
import json
import gdown
import traceback
import asyncio
import threading

app = FastAPI(
    title="Walmart Demand Forecasting API",
    description="Predict future sales using SARIMA & ARIMA models",
    version="1.0.0"
)

MODEL_PATH = "model.pkl"

# ── Cached forecast data ──
_cached_forecast = None
_forecast_ready = False
_forecast_error = None


def _compute_forecast_in_background():
    """Runs in a background thread — loads model, fits, caches result."""
    global _cached_forecast, _forecast_ready, _forecast_error
    try:
        print("Background: Starting forecast computation...")
        _cached_forecast = get_formatted_forecast()
        _forecast_ready = True
        _forecast_error = None
        print("Background: Forecast ready!")
    except Exception as e:
        _forecast_error = str(e)
        print(f"Background: Forecast failed: {e}")
        traceback.print_exc()


@app.on_event("startup")
def startup_event():
    """Download model and kick off async forecast computation."""
    global _cached_forecast, _forecast_ready

    # 1. Download model if needed
    if not os.path.exists(MODEL_PATH):
        print("Downloading model from Google Drive...")
        file_id = "1xgTR-zfUmGc59Y1CmTmv4wQ714kfJbnP"
        url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(url, MODEL_PATH, quiet=False)
        print("Model downloaded!")
    else:
        print(f"Model file exists at {MODEL_PATH}")

    # 2. Try loading from file cache first (instant, no model computation)
    cached = _load_cache()
    if cached is not None:
        _cached_forecast = cached
        _forecast_ready = True
        print("Forecast loaded from file cache — ready instantly!")
        return

    # 3. No file cache — start background thread to compute forecast
    #    This does NOT block server startup or any requests
    thread = threading.Thread(target=_compute_forecast_in_background, daemon=True)
    thread.start()
    print("Forecast computation started in background thread...")


# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(router, prefix='/api/v1')


# ── Forecast JSON endpoint (used by dashboard JS) ──────────────────────
@app.get("/api/v1/forecast", tags=["forecast"])
def get_forecast_json():
    """
    Returns forecast data as JSON.
    The dashboard JS calls this asynchronously.
    """
    global _cached_forecast, _forecast_ready, _forecast_error

    if _forecast_ready and _cached_forecast is not None:
        return JSONResponse(content=_cached_forecast)

    if _forecast_error:
        return JSONResponse(
            status_code=503,
            content={
                "error": _forecast_error,
                "message": "Forecast computation failed. Retrying...",
                "status": "error"
            }
        )

    # Still computing — tell the client to retry
    return JSONResponse(
        status_code=202,
        content={
            "message": "Forecast is being computed. Please retry in a few seconds.",
            "status": "computing"
        }
    )


# ── Forecast status endpoint (for polling) ──────────────────────────────
@app.get("/api/v1/forecast/status", tags=["forecast"])
def get_forecast_status():
    """Check if the forecast is ready."""
    if _forecast_ready:
        return {"status": "ready"}
    elif _forecast_error:
        return {"status": "error", "error": _forecast_error}
    else:
        return {"status": "computing"}


# ── Page routes ─────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def serve_index():
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
def serve_dashboard():
    return _build_dashboard()


@app.get("/dashboard.html", response_class=HTMLResponse, include_in_schema=False)
def serve_dashboard_html():
    return _build_dashboard()


def _build_dashboard():
    """
    Serve dashboard HTML immediately. Never blocks for forecast.
    If cached data is ready, inject it. Otherwise JS will fetch async.
    """
    with open("frontend/dashboard.html", "r", encoding="utf-8") as f:
        html = f.read()

    if _forecast_ready and _cached_forecast is not None:
        # Data is ready — inject it for instant load
        inject_script = f'<script>window.__FORECAST_DATA__ = {json.dumps(_cached_forecast)};</script>'
    else:
        # Not ready yet — JS will fetch from API asynchronously
        inject_script = '<script>window.__FORECAST_DATA__ = null;</script>'

    html = html.replace('</body>', f'{inject_script}\n</body>')
    return HTMLResponse(content=html)


# Static file mounts LAST (so routes above take priority)
app.mount("/images", StaticFiles(directory="."), name="images")
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
