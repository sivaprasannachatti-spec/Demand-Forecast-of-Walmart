import matplotlib.pyplot as plt

from src.components.data_ingestion import DataIngestion
from src.components.data_transformation import DataTransformation
from src.components.model_trainer import ModelTrainer

if __name__=="__main__":
    ingestionObj = DataIngestion()
    sales_train, prices_df, calendar_df = ingestionObj.dataIngestion()
    transformationObj = DataTransformation()
    final_df = transformationObj.dataTransformation(sales_df=sales_train, calendar_df=calendar_df)
    modelObj = ModelTrainer()
    print(modelObj.trainerConfig(final_df=final_df))