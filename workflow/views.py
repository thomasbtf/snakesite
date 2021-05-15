from typing import List
from django.views.generic import TemplateView, ListView, CreateView, DetailView, UpdateView, DeleteView
from .models import WorkflowTemplate, WorkflowTemplateSetting
from django.urls import reverse

class IndexView(TemplateView):
    template_name = "workflow/index.html"

class WorkflowTemplateListView(ListView):
    model = WorkflowTemplate
    paginate_by = 6

class WorkflowTemplateCreateView(CreateView):
    model = WorkflowTemplate
    fields = ["name", "description", "url", "contributors"]

class WorkflowTemplateUpdateView(UpdateView):
    model = WorkflowTemplate
    fields = ["name", "description", "url", "contributors"]

class WorkflowTemplateDetailView(DetailView):
    model = WorkflowTemplate

class WorkflowTemplateDeleteView(DeleteView):
    model = WorkflowTemplate

    def get_success_url(self):
        return reverse('workflow:templates')

class WorkflowTemplateSettingDetailView(DetailView):
    model = WorkflowTemplateSetting

class WorkflowTemplateSettingUpdateView(UpdateView):
    model = WorkflowTemplateSetting
    fields = ["path_snakefile", "path_sample_sheet", "path_config"]