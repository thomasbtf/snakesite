from django.contrib import admin

from .models import (RunInputFile, Result, Run, RunMessage, RunStatus, Workflow,
                     WorkflowTemplate, WorkflowStatus, WorkflowTemplateSetting)

for model in [Workflow, WorkflowTemplate, WorkflowStatus, Run, RunStatus, RunMessage, Result, RunInputFile, WorkflowTemplateSetting]:
    admin.site.register(model)
