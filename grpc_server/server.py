import os
from concurrent import futures

import grpc
import ml_service_pb2
import ml_service_pb2_grpc
from clearml import Model, Task

from ..service.app.ml.registry import get_model, list_models
from ..service.app.storage import delete_model as storage_delete_model
from ..service.app.storage import (
    dvc_add,
    dvc_list,
    dvc_remove,
    dvc_restore_file,
    load_model_from_clearml,
    save_model_clearml,
)

# ========================== Dataset Service ================================


class DatasetServiceServicer(ml_service_pb2_grpc.DatasetServiceServicer):
    def ListDatasets(self, request, context):
        datasets = dvc_list(path="data", recursive=True)
        return ml_service_pb2.DatasetList(datasets=datasets if datasets else [])

    def UploadDataset(self, request, context):
        filename = request.name
        path = f"/app/data/{filename}"
        os.makedirs("/app/data", exist_ok=True)
        with open(path, "wb") as f:
            f.write(request.content)
        dvc_add(path)
        return ml_service_pb2.SimpleResponse(status="ok", message="Uploaded")

    def DeleteDataset(self, request, context):
        name = request.name
        path = f"/app/data/{name}"
        dvc_remove(path)
        return ml_service_pb2.SimpleResponse(status="deleted", message=name)

    def DownloadDataset(self, request, context):
        filename = request.name
        try:
            file_path = dvc_restore_file(filename)
            with open(file_path, "rb") as f:
                content = f.read()
        except Exception as e:
            context.set_details(f"DVC error: {e}")
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return ml_service_pb2.FileContent()
        return ml_service_pb2.FileContent(content=content)


# ========================== Model Service ================================


class ModelServiceServicer(ml_service_pb2_grpc.ModelServiceServicer):
    def GetSupportedModels(self, request, context):
        models = list_models()
        return ml_service_pb2.ModelList(models=models if models else [])

    def GetTrainedModels(self, request, context):
        models = Model.query_models(only_published=True)
        models_info = []
        for m in sorted(
            models, key=lambda m: getattr(m, "last_update", ""), reverse=True
        ):
            models_info.append(m.name)
        return ml_service_pb2.ModelList(models=models_info)

    def TrainModel(self, request, context):
        model_class = request.model_class
        X = [list(f.values) for f in request.X]
        y = list(request.y)
        import json

        params = {}
        if request.params_json:
            params = json.loads(request.params_json)

        task = Task.init(
            project_name="ML_Service",
            task_name=f"train_{model_class}",
            task_type=Task.TaskTypes.training,
        )
        model = get_model(model_class)
        model.train(X, y, **params)
        output_model = save_model_clearml(model, model_class, task)
        task.upload_artifact(name=f"{model_class}_model_file", artifact_object=model)
        task.close()
        return ml_service_pb2.TrainResponse(
            status="trained", model_id=output_model.id, name=output_model.name
        )

    def Predict(self, request, context):
        X = [list(f.values) for f in request.X]
        try:
            model = load_model_from_clearml(request.model_name)
        except Exception as e:
            context.set_details(f"Model not found: {e}")
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return ml_service_pb2.PredictResponse()
        preds = model.predict(X)
        return ml_service_pb2.PredictResponse(predictions=[float(x) for x in preds])

    def DeleteModel(self, request, context):
        try:
            storage_delete_model(request.name)
            return ml_service_pb2.SimpleResponse(status="deleted", message=request.name)
        except FileNotFoundError:
            context.set_details("Model not found")
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return ml_service_pb2.SimpleResponse()


# ========================== Server Start ================================


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    ml_service_pb2_grpc.add_DatasetServiceServicer_to_server(
        DatasetServiceServicer(), server
    )
    ml_service_pb2_grpc.add_ModelServiceServicer_to_server(
        ModelServiceServicer(), server
    )
    server.add_insecure_port("[::]:50051")
    print("Starting gRPC server on :50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
