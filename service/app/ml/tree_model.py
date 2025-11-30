import pickle

from app.ml.base import BaseModel
from sklearn.tree import DecisionTreeRegressor


class TreeModel(BaseModel):
    name = "tree"

    def __init__(self):
        self.model = DecisionTreeRegressor()

    def train(self, X, y, **params):
        self.model = DecisionTreeRegressor(**params)
        self.model.fit(X, y)

    def predict(self, X):
        return self.model.predict(X).tolist()

    def save(self, path):
        with open(path, "wb") as f:
            pickle.dump(self.model, f)

    def load(self, path):
        with open(path, "rb") as f:
            self.model = pickle.load(f)
