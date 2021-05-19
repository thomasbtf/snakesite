from django.contrib import admin

from .models import (Result, Run, RunInputFile, RunMessage, RunStatus,
                     Workflow, WorkflowSetting, WorkflowStatus,
                     WorkflowTemplate, WorkflowTemplateSetting)

for model in [Workflow, WorkflowTemplate, WorkflowStatus, Run, RunStatus, RunMessage, Result, RunInputFile, WorkflowTemplateSetting, WorkflowSetting]:
    admin.site.register(model)
