import django
import workflow
from django.urls import reverse
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  TemplateView, UpdateView, FormView)
from .forms import InputFilesCreateForm, RunCreateForm
from .models import WorkflowSetting, WorkflowStatus, WorkflowTemplate, WorkflowTemplateSetting, Workflow, RunInputFile, Run
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages 
from django.contrib.auth.decorators import login_required
from django.db.models import Count


class IndexView(TemplateView):
    template_name = "workflow/index.html"


class DashboardView(TemplateView):
    template_name = "workflow/dashboard.html"


class WorkflowTemplateListView(ListView):
    model = WorkflowTemplate
    paginate_by = 6

    # def get_context_data(self, *args, **kwargs):
    #     context = super(WorkflowTemplateListView, self).get_context_data(*args,**kwargs)
    #     print(context)
    #     for obj in context["object_list"]:
    #        context[obj] = 98
    #     # run_instances = Workflow.objects.filter(id=workflow_instance.id)
    #     context["number_of_runs"] = 1
    #     return context


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

    def get_context_data(self, **kwargs):
        """
        This has been overridden to add `settings` to the template context
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


class WorkflowUpdateView(UpdateView):
    model = Workflow
    fields = ["name", "accessible_by"]
    template_name="workflow/workflow_update_form.html"


class WorkflowSettingUpdateView(UpdateView):
    model = WorkflowSetting
    fields = ["path_snakefile", "path_sample_sheet", "path_config"]
    template_name="workflow/workflowsetting_update_form.html"

@login_required
def create_run_view(request, workflow_id):
    workflow_instance = Workflow.objects.get(id = workflow_id)
    workflow_status = WorkflowStatus.objects.get(workflow_id=workflow_id)
    
    workflow_not_block = not (workflow_status.status != "RUNNING" or workflow_status.status != "QUEUED")

    if request.method == "POST":   
        run_form = RunCreateForm(request.POST, request.FILES)
        file_form = InputFilesCreateForm(request.POST, request.FILES)

        if run_form.is_valid() and file_form.is_valid() and workflow_not_block:
            # complete the run form
            run_instance = run_form.save(commit=False)
            run_instance.workflow = workflow_instance
            run_instance.created_by = request.user
            run_instance.save()

            # upload the files
            files = request.FILES.getlist('input_data')
            for f in files:
                file_instance = RunInputFile(input_data=f, run=run_instance)
                file_instance.save()

            # change status of workflow
            workflow_status.status = "RUNNING"
            workflow_status.save()

            messages.success(request, "Your run has been queued!" )
            # return redirect("workflow:workflows")
        
        if not run_form.is_valid():
            messages.error(request, "Unsuccessful run start. Please check the sample sheet, config, target or cores.")

        if not file_form.is_valid():
            messages.error(request, "Unsuccessful run start. Please check the input file.")

        if not workflow_not_block:
            messages.error(request, f"{ workflow_instance.name } is currently processing a run. Please wait for the old run to be completed before submitting a new one.")

    else:
        run_form = RunCreateForm()
        file_form = InputFilesCreateForm()

    context = {
        "run_form" : run_form,
        "file_form" : file_form,
        "workflow_instance": workflow_instance,
        "workflow_status" : workflow_status,
        "workflow_block" : not workflow_not_block,
    }

    return render(request, "workflow/run_form.html", context)


def create_to_feed(request):
    if request.method == 'POST':
        form = FeedModelForm(request.POST)
        file_form = FileModelForm(request.POST, request.FILES)
        files = request.FILES.getlist('file') #field name in model
        if form.is_valid() and file_form.is_valid():
            feed_instance = form.save(commit=False)
            feed_instance.user = user
            feed_instance.save()
            for f in files:
                file_instance = FeedFile(file=f, feed=feed_instance)
                file_instance.save()
    else:
        form = FeedModelForm()
        file_form = FileModelForm()