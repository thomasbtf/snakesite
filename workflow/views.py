from django.urls import reverse
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  TemplateView, UpdateView)

from .models import WorkflowSetting, WorkflowStatus, WorkflowTemplate, WorkflowTemplateSetting, Workflow


class IndexView(TemplateView):
    template_name = "workflow/index.html"


class DashboardView(TemplateView):
    template_name = "workflow/dashboard.html"


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


class WorkflowCreateView(CreateView):
    model = Workflow
    fields = ["workflow_template", "name"]

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class WorkflowDetailView(DetailView):
    model = Workflow
    context_object_name = 'settings'

    def get_context_data(self, **kwargs):
        """
        This has been overridden to add `settings` to the template context,
        """
        context = super().get_context_data(**kwargs)
        context['settings'] = WorkflowSetting.objects.get(workflow_id=self.object.pk)
        context['status'] = WorkflowStatus.objects.get(workflow_id=self.object.pk).get_status_display()
        return context


class WorkflowListView(ListView):
    model = Workflow
    paginate_by = 6


class WorkflowDeleteView(DeleteView):
    model = Workflow

    def get_success_url(self):
        return reverse('workflow:workflows')