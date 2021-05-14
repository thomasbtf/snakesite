from django.contrib import admin

from .models import (InputFile, Result, Run, RunMessage, RunStatus, Workflow,
                     WorkflowTemplate, WorkflowStatus)

for model in [Workflow, WorkflowTemplate, WorkflowStatus, Run, RunStatus, RunMessage, Result, InputFile]:
    admin.site.register(model)
