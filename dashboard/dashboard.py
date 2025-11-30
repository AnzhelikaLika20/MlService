import io
import json
import os

import pandas as pd
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://ml_service:8000")

st.set_page_config(page_title="ML Dashboard", layout="wide")

st.sidebar.title("ML Dashboard")
tab = st.sidebar.radio(
    "Выберите режим", ["Datasets", "Training", "Inference", "Status"]
)

HEADERS = {"accept": "application/json"}


#
# Helper functions
#
def _safe_get(path):
    try:
        r = requests.get(f"{API_URL}{path}", timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"GET {path} failed: {e}")
        return None


def _safe_post(path, json_payload=None, files=None):
    try:
        if files:
            r = requests.post(f"{API_URL}{path}", files=files, timeout=60)
        else:
            r = requests.post(f"{API_URL}{path}", json=json_payload, timeout=60)
        r.raise_for_status()
        return r.json()
    except requests.HTTPError as he:
        try:
            return {"error": r.text}
        except Exception as _:
            return {"error": str(he)}
    except Exception as e:
        return {"error": str(e)}


def _safe_delete(path):
    try:
        r = requests.delete(f"{API_URL}{path}", timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def _load_dvc_dataset(name):
    try:
        resp = requests.get(f"{API_URL}/datasets/{name}", timeout=10)
        resp.raise_for_status()
        content = resp.content
        if name.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(content))
        elif name.endswith(".json"):
            df = pd.read_json(io.BytesIO(content))
        else:
            st.error("Unknown file extension!")
            return None
        return df
    except Exception as e:
        st.error(f"Ошибка загрузки датасета {name}: {e}")
        return None


#
# Datasets tab
#
if tab == "Datasets":
    st.title("Datasets (DVC-backed)")
    st.info(
        "Список датасетов, загруженных через DVC. Загрузите CSV или JSON (строго CSV с header или JSON-список объектов)."
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("Available datasets on server (DVC)")
        data_list = _safe_get("/datasets")
        if data_list is None:
            st.write("Ошибка при получении списка датасетов.")
        else:
            if isinstance(data_list, dict) and data_list.get("error"):
                st.error(data_list["error"])
            else:
                if isinstance(data_list, list) and data_list:
                    for name in data_list:
                        st.write("•", name)
                else:
                    st.write("Нет датасетов")

    with col2:
        st.subheader("Upload dataset (CSV / JSON)")
        uploaded = st.file_uploader("Выберите CSV/JSON", type=["csv", "json"])
        if st.button("Upload dataset") and uploaded:
            try:
                files = {"file": (uploaded.name, uploaded.getvalue())}
                res = _safe_post("/datasets", files=files)
                if res and res.get("status") == "ok":
                    st.success(f"Uploaded: {uploaded.name}")
                elif res and res.get("error"):
                    st.error(f"Upload failed: {res['error']}")
                else:
                    st.write(res)
            except Exception as e:
                st.error(f"Upload error: {e}")

    st.markdown("---")
    st.subheader("Delete dataset")
    if isinstance(data_list, list) and data_list:
        del_name = st.selectbox("Select dataset to delete", options=data_list, index=0)
        if st.button("Delete selected dataset"):
            resp = _safe_delete(f"/datasets/{del_name}")
            if resp and resp.get("status") == "deleted":
                st.success(f"Deleted {del_name}")
            else:
                st.error(f"Delete failed: {resp}")
    else:
        st.write("Нет доступных для удаления датасетов.")

#
# Training tab
#
elif tab == "Training":
    st.title("Train Model")
    st.info(
        "Выберите модель и датасет (DVC, upload или raw JSON). Настройте фичи/таргет и гиперпараметры."
    )

    supported = _safe_get("/models/supported-models")
    models_list = supported.get("models") if supported else []
    if not models_list:
        st.warning(
            "Не удалось получить список моделей или список пуст. Проверьте /models/supported-models"
        )
        models_list = []

    model_choice = st.selectbox("Model class", options=models_list)

    st.markdown("### Data input")
    train_mode = st.radio(
        "Source of training data",
        ["Select DVC dataset", "Upload file (CSV/JSON)", "Paste X and y JSON"],
    )
    df = None
    feature_cols = []
    target_col = None
    if train_mode == "Select DVC dataset":
        dvc_datasets = _safe_get("/datasets")
        if isinstance(dvc_datasets, dict) and dvc_datasets.get("error"):
            st.error(dvc_datasets["error"])
            dvc_datasets = []
        ds_name = st.selectbox(
            "Выбери датасет (DVC)", options=dvc_datasets if dvc_datasets else []
        )
        if ds_name:
            df = _load_dvc_dataset(ds_name)
            if df is not None:
                st.dataframe(df.head())
                cols = df.columns.tolist()
                feature_cols = st.multiselect(
                    "Feature columns (X)", options=cols, default=[c for c in cols[:-1]]
                )
                target_col = st.selectbox(
                    "Target column (y)",
                    options=[c for c in cols if c not in feature_cols],
                )
    elif train_mode == "Upload file (CSV/JSON)":
        file = st.file_uploader(
            "Upload dataset for training", type=["csv", "json"], key="trainfile"
        )
        if file:
            st.markdown("Preview")
            try:
                if file.type == "application/json" or file.name.endswith(".json"):
                    df = pd.read_json(io.BytesIO(file.getvalue()))
                else:
                    df = pd.read_csv(io.BytesIO(file.getvalue()))
                st.dataframe(df.head())
                cols = df.columns.tolist()
                feature_cols = st.multiselect(
                    "Feature columns (X)", options=cols, default=[c for c in cols[:-1]]
                )
                target_col = st.selectbox(
                    "Target column (y)",
                    options=[c for c in cols if c not in feature_cols],
                )
            except Exception as e:
                st.error(f"Failed to parse file: {e}")
                df = None
    else:
        st.markdown("Paste X and y as JSON arrays")
        x_text = st.text_area("X (JSON array, e.g. [[1,2],[3,4]])", height=120)
        y_text = st.text_area("y (JSON array, e.g. [0,1])", height=80)

    st.markdown("### Hyperparameters (JSON)")
    params_text = st.text_area("params", value="{}", height=120)
    params = {}
    params_error = None
    try:
        params = json.loads(params_text) if params_text.strip() else {}
        if not isinstance(params, dict):
            params_error = "params must be a JSON object (dict)"
    except Exception as e:
        params_error = str(e)
    if params_error:
        st.error(f"Invalid params JSON: {params_error}")

    if st.button("Train"):
        if not model_choice:
            st.error("Выберите модель")
        else:
            if train_mode in ["Select DVC dataset", "Upload file (CSV/JSON)"]:
                if df is None:
                    st.error("Загрузите корректный файл/датасет")
                else:
                    try:
                        if not feature_cols:
                            st.error(
                                "Выберите хотя бы одну колонку как признак (feature)"
                            )
                            st.stop()
                        if not target_col:
                            st.error("Выберите колонку-таргет (y)")
                            st.stop()
                        if target_col in feature_cols:
                            st.error("Таргет не должен входить в признаки")
                            st.stop()
                        X = df[feature_cols].values.tolist()
                        y = df[target_col].values.ravel().tolist()
                        X = X[0] if len(X) else X
                        payload = {"X": X, "y": y, "params": params}
                        with st.spinner("Training..."):
                            res = _safe_post(
                                f"/models/{model_choice}/train", json_payload=payload
                            )
                        if res and res.get("status") == "trained":
                            st.success(
                                f"Trained. Model id: {res.get('model_id')}, name: {res.get('name')}"
                            )
                        else:
                            st.error(f"Train failed: {res}")
                    except Exception as e:
                        st.error(f"Error preparing data: {e}")
            else:
                try:
                    X = json.loads(x_text)
                    y = json.loads(y_text)
                    payload = {"X": X, "y": y, "params": params}
                except Exception as e:
                    st.error(f"Invalid JSON for X/y: {e}")
                else:
                    with st.spinner("Training..."):
                        res = _safe_post(
                            f"/models/{model_choice}/train", json_payload=payload
                        )
                    if res and res.get("status") == "trained":
                        st.success(
                            f"Trained. Model id: {res.get('model_id')}, name: {res.get('name')}"
                        )
                    else:
                        st.error(f"Train failed: {res}")

#
# Inference tab
#
elif tab == "Inference":
    st.title("Inference")
    st.info(
        "Выберите модель (из ClearML), используйте DVC-датасет или введите X вручную."
    )

    trained = _safe_get("/models/trained-models")
    trained_models = trained.get("models") if trained else []
    model_map = {}
    model_names = []
    if isinstance(trained_models, list):
        for m in trained_models:
            name = m.get("name") or m.get("id")
            model_names.append(name)
            model_map[name] = m

    model_choice = st.selectbox("Select trained model", options=model_names)
    use_dvc_ds = st.checkbox("Использовать DVC датасет для X", value=False)
    X = None
    if use_dvc_ds:
        dvc_datasets = _safe_get("/datasets")
        ds_name = st.selectbox(
            "Выбери DVC датасет",
            options=dvc_datasets if dvc_datasets else [],
            key="inferdataset",
        )
        if ds_name:
            df = _load_dvc_dataset(ds_name)
            if df is not None:
                st.dataframe(df.head())
                cols = df.columns.tolist()
                feature_cols = st.multiselect(
                    "Feature columns (X)", options=cols, default=[c for c in cols]
                )
                if feature_cols:
                    X = df[feature_cols].values.tolist()
                    X = X[0] if len(X) else X
    else:
        x_input = st.text_area("X (JSON array):", value="[[1,2],[3,4]]", height=150)
        if x_input:
            try:
                X = json.loads(x_input)
            except Exception as e:
                st.error(f"Invalid JSON: {e}")

    if st.button("Predict"):
        if not model_choice:
            st.error("Выберите модель")
        else:
            if X is None:
                st.error("Нет данных X для предсказания")
            else:
                backend_model_name = (
                    model_map.get(model_choice, {}).get("name") or model_choice
                )
                with st.spinner("Requesting predictions..."):
                    res = _safe_post(
                        f"/models/{backend_model_name}/predict", json_payload={"X": X}
                    )
                if res and res.get("predictions") is not None:
                    st.success("Predictions:")
                    st.write(res["predictions"])
                else:
                    st.error(f"Prediction failed: {res}")

elif tab == "Status":
    st.title("Service status / info")
    st.write("API URL:", API_URL)

    st.subheader("Health check")
    try:
        r = requests.get(f"{API_URL}/health", timeout=3)
        if r.ok:
            data = r.json()
            status_str = data.get("status", "unknown")
            st.success(f"Health: {status_str}")
            st.write(data)
        else:
            st.error(f"Health: {r.status_code}")
            st.write(r.text)
    except Exception as e:
        st.error(f"Health check failed: {e}")

    st.write(
        "При проблемах проверьте выполнение шагов из README, переменные окружения и доступность ClearML"
    )
