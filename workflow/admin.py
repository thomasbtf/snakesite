from django.contrib import admin

from .models import (Result, Run, RunInputFile, RunMessage, RunStatus,
                     Workflow, WorkflowStatus, WorkflowTemplate,
                     WorkflowTemplateSetting, WorkflowSetting)

for model in [Workflow, WorkflowTemplate, WorkflowStatus, Run, RunStatus, RunMessage, Result, RunInputFile, WorkflowTemplateSetting, WorkflowSetting]:
    admin.site.register(model)
