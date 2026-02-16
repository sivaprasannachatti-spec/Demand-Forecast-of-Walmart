import sys
import os
import joblib

from src.exception import CustomException
from src.logger import logging

# Cache: load the model only once, reuse on subsequent calls
_cached_model = None

def loadModel():
    global _cached_model
    if _cached_model is not None:
        return _cached_model

    try:
        MODEL_PATH = 'model.pkl'
        logging.info(f"Loading model from {MODEL_PATH}...")
        _cached_model = joblib.load(MODEL_PATH)
        logging.info("Model loaded and cached successfully")
        return _cached_model
    except Exception as e:
        raise CustomException(e, sys)