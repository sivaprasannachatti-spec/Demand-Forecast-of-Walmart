import sys
import dill

from src.exception import CustomException

def loadModel():
    try:
        MODEL_PATH = 'artifacts/model.pkl'
        with open(MODEL_PATH, 'rb') as f:
            model = dill.load(f)
        return model
    except Exception as e:
        raise CustomException(e, sys)