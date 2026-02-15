import sys

from src.exception import CustomException
from src.logger import logging
from backend.utils.loadModel_utils import *
from backend.services.forecast_service import getForecast

def predictSales():
    try:
        preds = getForecast()
        logging.info("Forecast received successfully")
        return {
            "status": "successfull",
            "message": "Forecast generated successfully",
            "data": preds
        }
    except Exception as e:
        raise CustomException(e, sys)