from django.urls import path
from .views import IndexView, WorkflowTemplateListView, WorkflowTemplateCreateView, WorkflowTemplateDetailView, WorkflowTemplateUpdateView, WorkflowTemplateDeleteView, WorkflowTemplateSettingDetailView, WorkflowTemplateSettingUpdateView

app_name="workflow"

urlpatterns = [
    path('', IndexView.as_view(), name="index"),
    path('template/', WorkflowTemplateListView.as_view(), name="templates"),
    path('template/<int:pk>/', WorkflowTemplateDetailView.as_view(), name="template-detail"),
    path('template/<int:pk>/update', WorkflowTemplateUpdateView.as_view(), name="template-update"),
    path('template/<int:pk>/delete', WorkflowTemplateDeleteView.as_view(), name="template-delete"),
    path('template/setting/<int:pk>/', WorkflowTemplateSettingDetailView.as_view(), name="template-setting"),
    path('template/setting/<int:pk>/update/', WorkflowTemplateSettingUpdateView.as_view(), name="template-setting-update"),
    path('template/new/', WorkflowTemplateCreateView.as_view(), name="template-create"),
]