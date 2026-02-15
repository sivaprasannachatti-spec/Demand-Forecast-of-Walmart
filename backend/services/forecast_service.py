import sys
import numpy as np

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
        for date, value in preds.items():
            forecast_data.append({
                "date": str(date.date()),
                "predicted_sales": round(float(value), 2)
            })

        total_predicted = round(float(preds.sum()), 2)
        avg_predicted = round(float(preds.mean()), 2)

        return {
            "forecast": forecast_data,
            "summary": {
                "total_predicted_sales": total_predicted,
                "avg_predicted_sales": avg_predicted,
                "forecast_days": len(forecast_data)
            }
        }
    except Exception as e:
        raise CustomException(e, sys)