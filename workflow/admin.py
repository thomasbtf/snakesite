from django.contrib import admin

from .models import (Result, Run, RunInputFile, RunMessage, RunStatus,
                     Workflow, WorkflowStatus, WorkflowTemplate,
                     WorkflowTemplateSetting)

for model in [Workflow, WorkflowTemplate, WorkflowStatus, Run, RunStatus, RunMessage, Result, RunInputFile, WorkflowTemplateSetting]:
    admin.site.register(model)
