from django.urls import path

from .views import CreateWorkflowView, ServiceInfoView, UpdateWorkflowStatusView

app_name = "wms_api"

urlpatterns = [
    path("api/service-info/", ServiceInfoView.as_view(), name="service-info"),
    path("create_workflow/", CreateWorkflowView.as_view(), name="create-workflow"),
    path(
        "update_workflow_status",
        UpdateWorkflowStatusView.as_view(),
        name="update-workflow-status",
    ),
]
