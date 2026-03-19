# Добавить сохранение дистиллированных моделей
class ModelRegistry:
    # ...

    def add_distilled_model(self, distilled_model):
        self.distilled_models[distilled_model.id] = distilled_model

    def get_distilled_model(self, model_id):
        return self.distilled_models.get(model_id)