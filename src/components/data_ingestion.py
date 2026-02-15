import os
import sys
import numpy as np
import pandas as pd

from src.logger import logging
from src.exception import CustomException
from dataclasses import dataclass
from src.components.data_transformation import DataTransformation
from src.components.model_trainer import ModelTrainer

@dataclass
class DataIngestionConfig:
    sales_path = os.path.join("artifacts", "sales_train.csv")
    prices_path = os.path.join("artifacts", "prices.csv")
    calendar_path = os.path.join("artifacts", "calendar.csv")

class DataIngestion:
    def __init__(self):
        self.ingestion_config = DataIngestionConfig()
    
    def dataIngestion(self):
        try:
            sales_df = pd.read_csv(r'C:\Users\shiva\OneDrive\Documents\Demand Forecasting of Walmart\notebook\sales_train_validation.csv', encoding='latin')
            calendar_df = pd.read_csv(r'C:\Users\shiva\OneDrive\Documents\Demand Forecasting of Walmart\notebook\calendar.csv', encoding='latin')
            prices_df = pd.read_csv(r'C:\Users\shiva\OneDrive\Documents\Demand Forecasting of Walmart\notebook\sell_prices.csv', encoding='latin')
            logging.info("All datasets loaded successfully")
            os.makedirs(os.path.dirname(self.ingestion_config.sales_path), exist_ok=True)
            sales_df.to_csv(self.ingestion_config.sales_path, index=True)
            prices_df.to_csv(self.ingestion_config.prices_path, index=True)
            calendar_df.to_csv(self.ingestion_config.calendar_path, index=True)
            logging.info("All datasets stored successfully")
            return(
                sales_df,
                prices_df,
                calendar_df
            )
        except Exception as e:
            raise CustomException(e, sys)