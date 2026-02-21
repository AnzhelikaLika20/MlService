from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class DistillationConfig:
    temperature: float = None
    alpha: float = None
    epochs: int = None
    learning_rate: float = None
    batch_size: int = None
    validation_split: float = None

@dataclass
class DistillationMetrics:
    teacher_metrics: List[float] = field(default_factory=list)
    student_metrics: List[float] = field(default_factory=list)
    distillation_loss: List[float] = field(default_factory=list)
    accuracy_preserved: bool = False
    size_reduction: float = None
    speedup: float = None

@dataclass
class DistillationResult:
    distillation_id: str = None
    teacher_model_id: int = None
    student_model_id: int = None
    config: DistillationConfig = None
    metrics: DistillationMetrics = None
    status: str = None

class DistillationManager:
    def start_distillation(self, teacher_model_id, student_model_type, dataset_name, config):
        # ...

    def get_result(self, distillation_id):
        # ...

    def list_distillations(self):
        # ...