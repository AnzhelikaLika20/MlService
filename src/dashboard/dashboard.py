# Добавить вкладку дистилляции
from .distillation import distillation_tab

app.layout = web.Row(
    # ...
    tab1=distillation_tab,
)