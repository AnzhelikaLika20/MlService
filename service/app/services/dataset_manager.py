import os

DATASETS_PATH = "data"

class DatasetManager:

    @staticmethod
    def list_datasets():
        if not os.path.exists(DATASETS_PATH):
            return []
        return os.listdir(DATASETS_PATH)
