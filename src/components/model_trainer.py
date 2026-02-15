import os
import sys
import torch
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sklearn

from src.logger import logging
from src.exception import CustomException
from dataclasses import dataclass
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import adfuller
from sklearn.metrics import root_mean_squared_error, mean_absolute_error, mean_absolute_percentage_error
from src.utils import *

@dataclass
class ModelTrainerConfig:
    model_path = os.path.join("artifacts", "model.pkl")

class ModelTrainer:
    def __init__(self):
        self.trainer_config = ModelTrainerConfig()

    def evaluateModel(self, true_values, predicted_values):
        try:
            rmse = root_mean_squared_error(true_values, predicted_values)
            mae = mean_absolute_error(true_values, predicted_values)
            mape = mean_absolute_percentage_error(true_values, predicted_values)
            return(
                rmse,
                mae,
                mape
            )
        except Exception as e:
            raise CustomException(e, sys)
    
    def trainerConfig(self, final_df):
        try:
            result = adfuller(final_df['TotalSales'])
            final_df['diff_sales'] = final_df['TotalSales'].diff()
            final_df = final_df.dropna()
            train_df = final_df[:-30]
            test_df = final_df[-30:]
            model = SARIMAX(
                train_df['TotalSales'],
                order=(1,1,1),
                seasonal_order=(1,2,2,7)
            )
            result = model.fit()
            forecast = result.forecast(steps=30)
            forecast_predicted = np.expm1(forecast)
            actual = np.expm1(test_df['TotalSales'])
            os.makedirs(os.path.dirname(self.trainer_config.model_path), exist_ok=True)
            save_object(
                file_path=self.trainer_config.model_path,
                obj = model
            )
            return forecast_predicted
        except Exception as e:
            raise CustomException(e, sys)