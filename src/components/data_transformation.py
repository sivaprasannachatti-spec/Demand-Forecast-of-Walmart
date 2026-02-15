import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sklearn
import seaborn as sns

from src.logger import logging
from src.exception import CustomException
from dataclasses import dataclass
from src.utils import *

@dataclass
class DataTransformationConfig:
    transformation_path = os.path.join("artifacts", "data_cleaning.pkl")

class DataTransformation:
    def __init__(self):
        self.transformation_config = DataTransformationConfig()
    
    def dataTransformation(self, sales_df, calendar_df):
        try:
            calendar_df['event_name_1'] = calendar_df['event_name_1'].fillna("No_event")
            calendar_df['event_type_1'] = calendar_df['event_type_1'].fillna("No_event")
            calendar_df['event_name_2'] = calendar_df['event_name_2'].fillna("No_event")
            calendar_df['event_type_2'] = calendar_df['event_type_2'].fillna("No_event")
            logging.info("Calendar null values handled successfully")
            sales_df = sales_df.melt(
                id_vars=['id', 'item_id', 'dept_id', 'cat_id', 'store_id', 'state_id'],
                var_name='d',
                value_name='TotalSales'
            )
            logging.info('Converted the sales data into long format i.e date-->sales')
            sales_df = sales_df.merge(calendar_df, on='d')
            logging.info("Sales data merged successfully with calendar data")
            sales = sales_df.groupby("date")['TotalSales'].sum()
            final_df = sales.reset_index()
            final_df = final_df.sort_values("date")
            final_df.set_index("date", inplace=True)
            final_df['TotalSales'] = np.log1p(final_df['TotalSales']) 
            logging.info("Final dataset created successfully")
            return(
                final_df
            )
        except Exception as e:
            raise CustomException(e, sys)