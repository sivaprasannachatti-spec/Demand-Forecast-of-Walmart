from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from backend.routes.forecast_route import router 
import os
import gdown
import joblib

app = FastAPI(
    title="Walmart Demand Forecasting API",
    description="Predict future sales using SARIMA & ARIMA models",
    version="1.0.0"
)

MODEL_PATH = "model.pkl"

# Download model from Google Drive if not present locally
if not os.path.exists(MODEL_PATH):
    print("Downloading model from Google Drive...")
    file_id = "1xgTR-zfUmGc59Y1CmTmv4wQ714kfJbnP"
    url = f"https://drive.google.com/uc?id={file_id}"
    gdown.download(url, MODEL_PATH, quiet=False)
    print("Model downloaded successfully!")

print("Loading model...")
model = joblib.load(MODEL_PATH)
print("Model loaded successfully")



# Enable CORS so the frontend can call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes (must be registered BEFORE static file mounts)
app.include_router(router, prefix='/api/v1')

# Serve the ARIMA/SARIMA images
app.mount("/images", StaticFiles(directory="."), name="images")

# Serve the frontend static files (CSS, JS)
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Serve index.html for the root route
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def serve_index():
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

# Serve dashboard.html (both routes for Live Server & FastAPI compatibility)
@app.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
@app.get("/dashboard.html", response_class=HTMLResponse, include_in_schema=False)
def serve_dashboard():
    with open("frontend/dashboard.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())
