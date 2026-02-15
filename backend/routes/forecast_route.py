import sys

from fastapi import APIRouter
from src.exception import CustomException
from backend.controllers.forecast_controller import predictSales

router = APIRouter()

@router.get("/predict_sales", tags=['predict'])
def getSales():
    try:
        return predictSales()
    except Exception as e:
        raise CustomException(e, sys)
