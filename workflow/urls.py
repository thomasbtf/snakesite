from workflow.models import Result
from django.urls import path

from .views import (IndexView, DashboardView, WorkflowTemplateCreateView,
                    WorkflowTemplateDeleteView, WorkflowTemplateDetailView,
                    WorkflowTemplateListView,
                    WorkflowTemplateSettingDetailView,
                    WorkflowTemplateSettingUpdateView,
                    WorkflowTemplateUpdateView,
                    WorkflowCreateView,
                    WorkflowDetailView,
                    WorkflowListView,
                    WorkflowDeleteView,
                    WorkflowUpdateView,
                    WorkflowSettingUpdateView,
                    WorkflowCreateViewByTemplate,
                    create_run_view,
                    RunDetailView,
                    RunDeleteView,
                    RunListView,
                    ResultListView,
                    ResultDetailsView,)

app_name="workflow"

urlpatterns = [
    path('', IndexView.as_view(), name="index"),
    path('dashboard/', DashboardView.as_view(), name="dashboard"),
    path('template/new/', WorkflowTemplateCreateView.as_view(), name="template-create"),
    path('templates/', WorkflowTemplateListView.as_view(), name="templates"),
    path('template/<int:pk>/', WorkflowTemplateDetailView.as_view(), name="template-detail"),
    path('template/<int:pk>/update/', WorkflowTemplateUpdateView.as_view(), name="template-update"),
    path('template/<int:pk>/delete/', WorkflowTemplateDeleteView.as_view(), name="template-delete"),
    path('template/setting/<int:pk>/', WorkflowTemplateSettingDetailView.as_view(), name="template-setting"),
    path('template/setting/<int:pk>/update/', WorkflowTemplateSettingUpdateView.as_view(), name="template-setting-update"),
    path('workflows/', WorkflowListView.as_view(), name="workflows"),
    path('workflow/new/', WorkflowCreateView.as_view(), name="workflow-create"),
    path('workflow/new/<int:template_id>/', WorkflowCreateViewByTemplate.as_view(), name="workflow-create"),
    path('workflow/<int:pk>/', WorkflowDetailView.as_view(), name="workflow-detail"),
    path('workflow/<int:pk>/update/', WorkflowUpdateView.as_view(), name="workflow-update"),
    path('workflow/<int:pk>/delete/', WorkflowDeleteView.as_view(), name="workflow-delete"),
    path('workflow/setting/<int:pk>/update/', WorkflowSettingUpdateView.as_view(), name="workflow-setting-update"),
    path('runs/', RunListView.as_view(), name="runs"),
    path('run/new/<int:workflow_id>/', create_run_view, name="run-create"),
    path('run/<int:pk>/', RunDetailView.as_view(), name="run-details"),
    path('run/<int:pk>/delete/', RunDeleteView.as_view(), name="run-delete"),
    path('results/', ResultListView.as_view(), name="results"),
    path('results/<int:pk>/', ResultDetailsView.as_view(), name="results-details"),
]
