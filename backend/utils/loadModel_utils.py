import sys
import dill

from src.exception import CustomException
from src.logger import logging

_cached_model = None

def loadModel():
    global _cached_model
    if _cached_model is not None:
        return _cached_model

    try:
        MODEL_PATH = 'model.pkl'
        logging.info(f"Loading model from {MODEL_PATH}...")
        with open(MODEL_PATH, 'rb') as f:
            _cached_model = dill.load(f)
        logging.info("Model loaded and cached successfully")
        return _cached_model
    except Exception as e:
        raise CustomException(e, sys)