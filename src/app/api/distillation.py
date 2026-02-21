from fastapi import FastAPI, HTTPException
from .distillation import DistillationManager

app = FastAPI()

@app.post("/models/distill/start")
async def start_distillation(teacher_model_id: int, student_model_type: str, dataset_name: str, config: Dict):
    # ...
    return {"distillation_id": distillation_id, "status": status}

@app.get("/models/distill/{distillation_id}")
async def get_result(distillation_id: str):
    # ...

@app.get("/models/distill/list")
async def list_distillations():
    # ...

@app.delete("/models/distill/{distillation_id}")
async def delete_result(distillation_id: str):
    # ...