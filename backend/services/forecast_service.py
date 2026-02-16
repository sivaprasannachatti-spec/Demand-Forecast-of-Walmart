import sys
import numpy as np
from datetime import datetime, timedelta

from src.exception import CustomException
from src.logger import logging
from backend.utils.loadModel_utils import *

def getForecast():
    try:
        model = loadModel()
        logging.info("Model loaded successfully")
        preds = model.forecast(steps=30)
        preds = np.expm1(preds)
        logging.info("Next sales predicted successfully")

        # Convert to JSON-serializable format
        forecast_data = []

        # Check if preds has a DatetimeIndex (pandas Series) or is a plain array
        if hasattr(preds, 'index') and hasattr(preds.index, 'date'):
            # Pandas Series with DatetimeIndex
            for date, value in preds.items():
                forecast_data.append({
                    "date": str(date.date()),
                    "predicted_sales": round(float(value), 2)
                })
        else:
            # Plain array — generate dates starting from today
            start_date = datetime.now().date()
            values = preds if hasattr(preds, '__iter__') else [preds]
            for i, value in enumerate(values):
                forecast_date = start_date + timedelta(days=i + 1)
                forecast_data.append({
                    "date": str(forecast_date),
                    "predicted_sales": round(float(value), 2)
                })

        total_predicted = round(float(sum(item["predicted_sales"] for item in forecast_data)), 2)
        avg_predicted = round(total_predicted / len(forecast_data), 2) if forecast_data else 0

        logging.info(f"Forecast data generated: {len(forecast_data)} days")

        return {
            "forecast": forecast_data,
            "summary": {
                "total_predicted_sales": total_predicted,
                "avg_predicted_sales": avg_predicted,
                "forecast_days": len(forecast_data)
            }
        }
    except Exception as e:
        logging.error(f"Forecast error: {str(e)}")
        raise CustomException(e, sys)