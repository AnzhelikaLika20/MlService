from abc import ABC, abstractmethod

class BaseModel(ABC):
    name: str

    @abstractmethod
    def train(self, X, y, **params):
        pass

    @abstractmethod
    def predict(self, X):
        pass

    @abstractmethod
    def save(self, path: str):
        pass

    @abstractmethod
    def load(self, path: str):
        pass
