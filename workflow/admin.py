from django.contrib import admin

from .models import (Result, Run, RunInputFile, RunMessage, RunProgress,
                     RunStatus, Workflow, WorkflowSetting, WorkflowStatus,
                     WorkflowTemplate, WorkflowTemplateSetting)

admin.site.register([
    Workflow,
    WorkflowTemplate,
    WorkflowStatus,
    Run,
    RunStatus,
    RunMessage,
    RunProgress,
    Result,
    RunInputFile,
    WorkflowTemplateSetting,
    WorkflowSetting,
])
