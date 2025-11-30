import pickle

from app.ml.base import BaseModel
from sklearn.linear_model import LinearRegression


class LinearModel(BaseModel):
    name = "linear"

    def __init__(self):
        self.model = LinearRegression()

    def train(self, X, y, **params):
        self.model.fit(X, y)

    def predict(self, X):
        return self.model.predict(X).tolist()

    def save(self, path):
        with open(path, "wb") as f:
            pickle.dump(self.model, f)

    def load(self, path):
        with open(path, "rb") as f:
            self.model = pickle.load(f)
