class BaseModelSpec:
    name: str
    description: str
    hyperparameters: dict


class RandomForestSpec(BaseModelSpec):
    name = "random_forest"
    description = "Sklearn RandomForestClassifier"
    hyperparameters = {
        "n_estimators": "int",
        "max_depth": "int",
        "min_samples_split": "int"
    }


class LogisticRegressionSpec(BaseModelSpec):
    name = "logistic_regression"
    description = "Sklearn Logistic Regression"
    hyperparameters = {
        "C": "float",
        "max_iter": "int"
    }


class ModelRegistry:

    _models = [
        RandomForestSpec,
        LogisticRegressionSpec
    ]

    @classmethod
    def list_models(cls):
        result = []
        for model in cls._models:
            result.append({
                "name": model.name,
                "description": model.description,
                "hyperparameters": model.hyperparameters
            })
        return result
