from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from backend.routes.forecast_route import router
from backend.services.forecast_service import getForecast
import os
import json
import gdown

app = FastAPI(
    title="Walmart Demand Forecasting API",
    description="Predict future sales using SARIMA & ARIMA models",
    version="1.0.0"
)

MODEL_PATH = "model.pkl"

@app.on_event("startup")
def download_model():
    """Download model file on startup if it doesn't exist."""
    if not os.path.exists(MODEL_PATH):
        print("Downloading model from Google Drive...")
        file_id = "1xgTR-zfUmGc59Y1CmTmv4wQ714kfJbnP"
        url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(url, MODEL_PATH, quiet=False)
        print("Model downloaded!")
    else:
        print(f"Model file exists at {MODEL_PATH}")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes (keep for Swagger docs / external use)
app.include_router(router, prefix='/api/v1')

# Serve ARIMA/SARIMA images
app.mount("/images", StaticFiles(directory="."), name="images")

# Serve frontend static files (CSS, JS)
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Root → landing page
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def serve_index():
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

# Dashboard → inject forecast data directly into HTML (no fetch needed!)
@app.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
@app.get("/dashboard.html", response_class=HTMLResponse, include_in_schema=False)
def serve_dashboard():
    with open("frontend/dashboard.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Generate forecast and embed it in the page
    try:
        forecast_data = getForecast()
        data_json = json.dumps(forecast_data)
        # Inject data as a script tag before the closing </body>
        inject_script = f'<script>window.__FORECAST_DATA__ = {data_json};</script>'
        html = html.replace('</body>', f'{inject_script}\n</body>')
    except Exception as e:
        print(f"Error generating forecast: {e}")
        # If forecast fails, inject null so JS can show an error
        html = html.replace('</body>', '<script>window.__FORECAST_DATA__ = null;</script>\n</body>')

    return HTMLResponse(content=html)
