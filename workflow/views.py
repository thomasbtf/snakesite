from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from .forms import InputFilesCreateForm, RunCreateForm
from .models import (
    Result,
    Run,
    RunInputFile,
    Workflow,
    WorkflowSetting,
    WorkflowStatus,
    WorkflowTemplate,
    WorkflowTemplateSetting,
)


class IndexView(TemplateView):
    template_name = "workflow/index.html"


class DashboardView(ListView):
    model = Run
    ordering = ["-date_created"]
    template_name = "workflow/dashboard.html"


class WorkflowTemplateListView(ListView):
    model = WorkflowTemplate
    paginate_by = 6


class WorkflowTemplateCreateView(LoginRequiredMixin, CreateView):
    model = WorkflowTemplate
    fields = ["name", "description", "url", "contributors"]


class WorkflowTemplateUpdateView(LoginRequiredMixin, UpdateView):
    model = WorkflowTemplate
    fields = ["name", "description", "url", "contributors"]


class WorkflowTemplateDetailView(DetailView):
    model = WorkflowTemplate


class WorkflowTemplateDeleteView(LoginRequiredMixin, DeleteView):
    model = WorkflowTemplate

    def get_success_url(self):
        return reverse("workflow:templates")


class WorkflowTemplateSettingDetailView(DetailView):
    model = WorkflowTemplateSetting


class WorkflowTemplateSettingUpdateView(LoginRequiredMixin, UpdateView):
    model = WorkflowTemplateSetting
    fields = ["path_snakefile", "path_sample_sheet", "path_config"]


class WorkflowCreateView(LoginRequiredMixin, CreateView):
    model = Workflow
    fields = ["workflow_template", "name"]

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_initial(self):
        if self.kwargs.get("template_id"):
            workflow_template = get_object_or_404(
                WorkflowTemplate, pk=self.kwargs.get("template_id")
            )
            return {
                "workflow_template": workflow_template,
            }


class WorkflowDetailView(DetailView):
    model = Workflow


class WorkflowListView(ListView):
    model = Workflow
    paginate_by = 6


class WorkflowDeleteView(LoginRequiredMixin, DeleteView):
    model = Workflow

    def get_success_url(self):
        return reverse("workflow:workflows")


class WorkflowUpdateView(LoginRequiredMixin, UpdateView):
    model = Workflow
    fields = ["name", "accessible_by"]
    template_name = "workflow/workflow_update_form.html"


class WorkflowSettingUpdateView(LoginRequiredMixin, UpdateView):
    model = WorkflowSetting
    fields = ["path_snakefile", "path_sample_sheet", "path_config"]
    template_name = "workflow/workflowsetting_update_form.html"


@login_required
def run_create_view(request, workflow_id):
    workflow_instance = Workflow.objects.get(id=workflow_id)

    workflow_blocked = (
        workflow_instance.Status == "RUNNING" or workflow_instance.Status == "QUEUED"
    )

    if request.method == "POST":
        run_form = RunCreateForm(request.POST, request.FILES)
        file_form = InputFilesCreateForm(request.POST, request.FILES)

        if run_form.is_valid() and file_form.is_valid() and not workflow_blocked:
            # complete the run form
            run_instance = run_form.save(commit=False)
            run_instance.workflow = workflow_instance
            run_instance.created_by = request.user
            run_instance.save()

            # upload the files
            files = request.FILES.getlist("input_data")
            for f in files:
                file_instance = RunInputFile(input_data=f, run=run_instance)
                file_instance.save()

            # change status of workflow
            WorkflowStatus.objects.create(
                workflow=Workflow.objects.get(pk=workflow_id),
                status="QUEUED",
            )

            messages.success(request, "Your run has been queued!")
            return redirect("workflow:run-details", pk=run_instance.pk)

        if not run_form.is_valid():
            messages.error(
                request,
                "Unsuccessful run start. Please check the sample sheet, config, target or cores.",
            )

        if not file_form.is_valid():
            messages.error(
                request, "Unsuccessful run start. Please check the input file."
            )

        if workflow_blocked:
            messages.error(
                request,
                (
                    f"{ workflow_instance.name } is currently processing. ",
                    "Please wait for the old run to be completed before submitting a new one.",
                ),
            )

    else:
        run_form = RunCreateForm()
        file_form = InputFilesCreateForm()

    context = {
        "run_form": run_form,
        "file_form": file_form,
        "workflow_instance": workflow_instance,
        "workflow_status": workflow_instance.Status,
        "workflow_block": workflow_blocked,
    }

    return render(request, "workflow/run_form.html", context)


class RunDetailView(DetailView):
    model = Run

    def get_context_data(self, *args, **kwargs):
        context = super(RunDetailView, self).get_context_data(*args, **kwargs)
        context["run_list"] = Run.objects.all().order_by("-date_created")
        return context


class RunDeleteView(LoginRequiredMixin, DeleteView):
    model = Run

    def get_success_url(self):
        return reverse(
            "workflow:workflow-detail", kwargs={"pk": self.object.workflow.id}
        )


class RunListView(ListView):
    model = Run
    paginate_by = 6
    context_object_name = "run_list"
    ordering = ["-date_created"]


class ResultListView(ListView):
    model = Result
    paginate_by = 6
    ordering = ["-date_created"]


class ResultDetailsView(DetailView):
    model = Result


class MessageDetailView(DeleteView):
    model = Run
    template_name = "workflow/message_detail.html"


def report_view(request, pk):
    result = Result.objects.get(pk=pk)
    return render(request, result.path_index_report)


def download_report(request, pk):
    result = Result.objects.get(id=pk)
    filename = result.path_result_zip
    response = FileResponse(open(filename, "rb"))
    return response
