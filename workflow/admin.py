from django.contrib import admin
from .models import WorkflowRegistry, Workflow, WorkflowStatus, Run, RunStatus, RunMessage, Result

for model in [WorkflowRegistry, Workflow, WorkflowStatus, Run, RunStatus, RunMessage, Result]:
    admin.site.register(model)