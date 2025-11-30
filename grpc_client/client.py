import grpc
import ml_service_pb2
import ml_service_pb2_grpc

if __name__ == "__main__":
    channel = grpc.insecure_channel("ml_service:50001")

    stub = ml_service_pb2_grpc.ModelServiceStub(channel)

    response = stub.GetSupportedModels(ml_service_pb2.Empty())
    print("Model classes:", response.models)

    X = [
        ml_service_pb2.FeatureList(values=[1.0, 2.0]),
        ml_service_pb2.FeatureList(values=[3.0, 4.0]),
    ]
    y = [0.0, 1.0]
    params = '{"n_estimators": 5}'

    train_request = ml_service_pb2.TrainRequest(
        model_class="RandomForest", X=X, y=y, params_json=params
    )
    train_response = stub.TrainModel(train_request)
    print("Train response:", train_response)

    predict_request = ml_service_pb2.PredictRequest(model_name=train_response.name, X=X)
    pred_response = stub.Predict(predict_request)
    print("Predict:", pred_response.predictions)
