from django.contrib import admin

from .models import (InputFile, Result, Run, RunMessage, RunStatus, Workflow,
                     WorkflowRegistry, WorkflowStatus)

for model in [WorkflowRegistry, Workflow, WorkflowStatus, Run, RunStatus, RunMessage, Result, InputFile]:
    admin.site.register(model)
