from django.contrib import admin
from .models import WorkflowRegistry, Workflow, WorkflowStatus, Run, RunStatus, RunMessage, Result, InputFile

for model in [WorkflowRegistry, Workflow, WorkflowStatus, Run, RunStatus, RunMessage, Result, InputFile]:
    admin.site.register(model)