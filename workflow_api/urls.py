from django.urls import path
from .views import WorkflowTemplateView, RunView, ResultView

app_name="workflow_api"

urlpatterns = [
    path("workflow/", WorkflowTemplateView.as_view(), name="workflow"),
    path("run/", RunView.as_view(), name="run"),
    path("result/", ResultView.as_view(), name="result")
]