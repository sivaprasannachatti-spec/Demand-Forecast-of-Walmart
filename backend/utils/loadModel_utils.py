import sys
import os
import joblib
import numpy as np

from src.exception import CustomException
from src.logger import logging

def loadModel():
    try:
        MODEL_PATH = 'model.pkl'
        model = joblib.load(MODEL_PATH)
        return model
    except Exception as e:
        raise CustomException(e, sys)