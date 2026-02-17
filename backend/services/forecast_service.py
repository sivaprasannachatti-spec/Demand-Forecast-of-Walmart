import sys
import os
import time
import json
import numpy as np

from src.exception import CustomException
from src.logger import logging
from backend.utils.loadModel_utils import *

# Cache the fitted model so .fit() runs only ONCE per server lifecycle
_fitted_model = None

# File-based cache so predictions survive server restarts
FORECAST_CACHE_FILE = "forecast_cache.json"


def getForecast():
    """
    Generate 30-day forecast predictions.
    Uses in-memory cache first, then file cache, then computes fresh.
    """
    global _fitted_model
    try:
        if _fitted_model is None:
            model = loadModel()
            logging.info("Fitting model (one-time only)...")

            # Retry fitting up to 3 times (handles transient issues)
            last_error = None
            for attempt in range(1, 4):
                try:
                    _fitted_model = model.fit(disp=False)
                    logging.info("Model fitted and cached in memory")
                    break
                except Exception as fit_error:
                    last_error = fit_error
                    logging.info(f"Model fit attempt {attempt} failed: {fit_error}")
                    if attempt < 3:
                        time.sleep(1)

            if _fitted_model is None:
                raise last_error

        preds = _fitted_model.forecast(steps=30)
        preds = np.expm1(preds)
        logging.info("Next sales predicted successfully")
        return preds
    except Exception as e:
        raise CustomException(e, sys)


def get_formatted_forecast():
    """
    Returns the forecast as a ready-to-use dict with 'forecast' and 'summary'.
    Uses file-based caching so predictions survive server restarts.
    """
    from datetime import datetime, timedelta

    # 1. Try file cache first (instant, no model needed)
    cached = _load_cache()
    if cached is not None:
        logging.info("Forecast loaded from file cache")
        return cached

    # 2. Compute fresh forecast
    preds = getForecast()

    forecast_data = []
    if hasattr(preds, 'index') and hasattr(preds.index, 'date'):
        for date, value in preds.items():
            forecast_data.append({
                "date": str(date.date()),
                "predicted_sales": round(float(value), 2)
            })
    else:
        start_date = datetime.now().date()
        for i, value in enumerate(preds):
            forecast_date = start_date + timedelta(days=i + 1)
            forecast_data.append({
                "date": str(forecast_date),
                "predicted_sales": round(float(value), 2)
            })

    total_sales = round(sum(item["predicted_sales"] for item in forecast_data), 2)
    avg_sales = round(total_sales / len(forecast_data), 2)

    data = {
        "forecast": forecast_data,
        "summary": {
            "total_predicted_sales": total_sales,
            "avg_predicted_sales": avg_sales,
            "forecast_days": len(forecast_data)
        }
    }

    # 3. Save to file cache for next restart
    _save_cache(data)

    return data


def _load_cache():
    """Load forecast from file cache if it exists."""
    try:
        if os.path.exists(FORECAST_CACHE_FILE):
            with open(FORECAST_CACHE_FILE, "r") as f:
                data = json.load(f)
            if data and "forecast" in data and len(data["forecast"]) > 0:
                return data
    except Exception as e:
        logging.info(f"Could not load forecast cache: {e}")
    return None


def _save_cache(data):
    """Save forecast data to file cache."""
    try:
        with open(FORECAST_CACHE_FILE, "w") as f:
            json.dump(data, f)
        logging.info(f"Forecast cached to {FORECAST_CACHE_FILE}")
    except Exception as e:
        logging.info(f"Could not save forecast cache: {e}")