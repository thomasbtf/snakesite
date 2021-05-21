import os
import uuid

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.fields import PositiveSmallIntegerField
from django.db.models.fields.related import ForeignKey
from django.urls import reverse

from .storage import OverwriteStorage
from .utils import make_dir

from collections import defaultdict

WORKFLOW_STATUS_CHOICES = [
    ("CREATED", "Created"),
    ("TESTING", "Testing"),
    ("QUEUED", "Queued"),
    ("RUNNING", "Running"),
    ("AVAILABLE", "Available"),
    ("DEPRECATED", "Deprecated"),
]

RUN_STATUS_CHOICES = [
    ("CREATED", "Created"),
    ("QUEUED", "Queued"),
    ("TESTING", "Testing"),
    ("RUNNING", "Running"),
    ("REPORTING", "Generate Report"),
    ("FINISHED", "Finished"),
    ("FAILED", "Failed"),
]


def templates_path():
    DIR = settings.WORKFLOW_TEMPLATES
    make_dir(DIR)
    return DIR


def workflows_path():
    DIR = settings.WORKFLOWS
    make_dir(DIR)
    return DIR


def results_path():
    DIR = settings.RESULTS
    make_dir(DIR)
    return DIR


class WorkflowTemplate(models.Model):
    """
    Data about the workflow itself.
    """

    name = models.CharField(max_length=60, blank=False, unique=True)
    description = models.TextField(max_length=400, blank=False)
    url = models.URLField(blank=False)
    owner = models.ManyToManyField(
        User, blank=False, related_name="workflow_template_owner"
    )
    contributors = models.ManyToManyField(
        User, blank=True, related_name="workflow_template_contributors"
    )
    date_created = models.DateTimeField(auto_now_add=True, blank=False)
    date_modified = models.DateTimeField(auto_now=True, blank=False)

    def __str__(self) -> str:
        return f"Template {self.name}"

    def get_absolute_url(self):
        return reverse("workflow:template-detail", kwargs={"pk": self.pk})

    @property
    def NumWorkflows(self):
        return self.workflow_set.count()

    @property
    def NumRuns(self):
        return sum(
            child.NumRuns
            for child in self.workflow_set.all()
        )


class WorkflowTemplateSetting(models.Model):
    """
    Suggested settings of workflow.
    """

    workflow_template = models.ForeignKey(WorkflowTemplate, on_delete=models.CASCADE)
    path_snakefile = models.CharField(max_length=100, blank=False)
    path_sample_sheet = models.CharField(max_length=100, blank=False)
    path_config = models.CharField(max_length=100, blank=False)
    date_created = models.DateTimeField(auto_now_add=True, blank=False)
    storage_location = models.FilePathField(
        path=templates_path, allow_files=False, allow_folders=True, blank=False
    )

    def __str__(self) -> str:
        return f"{self.workflow_template} Setting"

    def get_absolute_url(self):
        return reverse("workflow:template-setting", kwargs={"pk": self.pk})


class Workflow(models.Model):
    """
    The local copy of a workflow.
    """

    workflow_template = models.ForeignKey(
        WorkflowTemplate,
        on_delete=models.SET_NULL,
        null=True,
        help_text="Select the template you want to use.",
    )
    name = models.CharField(
        max_length=60,
        blank=False,
        help_text='The name of your workflow. E.g. "SARS-CoV-2 Production".',
    )
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="workflow_owner"
    )
    accessible_by = models.ManyToManyField(
        User, blank=True, related_name="accessible_by"
    )
    date_created = models.DateTimeField(auto_now_add=True, blank=False)

    def __str__(self) -> str:
        return f"{self.pk} {self.name}"

    def get_absolute_url(self):
        return reverse("workflow:workflow-detail", kwargs={"pk": self.pk})

    @property
    def NumRuns(self):
        return self.run_set.count()

    @property
    def Status(self):
        return (
            self.workflowstatus_set.all()
            .order_by("-date_created")
            .first()
            .get_status_display()
        )

    @property
    def Setting(self):
        return WorkflowSetting.objects.get(workflow_id=self.pk)


class WorkflowSetting(models.Model):
    """
    Settings of a local workflow.
    """

    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE)
    storage_location = models.FilePathField(
        path=workflows_path, allow_files=False, allow_folders=True, blank=False
    )
    path_snakefile = models.CharField(max_length=100, blank=False)
    path_sample_sheet = models.CharField(max_length=100, blank=False)
    path_config = models.CharField(max_length=100, blank=False)

    def __str__(self) -> str:
        return f"Settings {self.workflow}"

    def get_absolute_url(self):
        return reverse("workflow:workflow-detail", kwargs={"pk": self.workflow.pk})


class WorkflowStatus(models.Model):
    """
    Represents the status of the local Workflow. Can change over time.
    """

    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=15, choices=WORKFLOW_STATUS_CHOICES, default="CREATED", blank=False
    )
    date_created = models.DateTimeField(auto_now_add=True, blank=False)

    def __str__(self) -> str:
        return f"{self.workflow} {self.status}"


def sample_sheet_path(instance, filename):
    settings = WorkflowSetting.objects.get(workflow_id=instance.workflow.id)
    return os.path.join(settings.storage_location, settings.path_sample_sheet)


def config_path(instance, filename):
    settings = WorkflowSetting.objects.get(workflow_id=instance.workflow.id)
    return os.path.join(settings.storage_location, settings.path_config)


class Run(models.Model):
    """
    Represent a run of a certain workflow.
    """

    workflow = ForeignKey(Workflow, on_delete=models.CASCADE)
    created_by = ForeignKey(User, on_delete=models.SET_NULL, null=True)
    sample_sheet = models.FileField(
        upload_to=sample_sheet_path,
        blank=False,
        max_length=200,
        storage=OverwriteStorage(),
        help_text='Required. Upload your sample sheet here. Paths to input data files must start with "data/".',
    )
    config = models.FileField(
        upload_to=config_path,
        max_length=200,
        storage=OverwriteStorage(),
        blank=True,
        help_text="Optional. Upload a changed config file here. Else the default config from the workflow is used.",
    )
    target = models.CharField(
        max_length=30,
        default="all",
        blank=False,
        help_text="Target(s) to build by snakemake. May be rules or files.",
    )
    cores = models.PositiveSmallIntegerField(
        default=6,
        blank=False,
        help_text="Number of maximum CPU cores/jobs running in parallel.",
    )
    args = models.CharField(
        max_length=200,
        default="--use-conda",
        blank=True,
        help_text="Snakemake command line options to start the run with.",
    )
    environment_variable = models.CharField(
        max_length=200,
        default="",
        blank=True,
        help_text="Environment variable(s), that are exported before the run starts. Format: {'foo' : 'bar', ...}",
    )  # TODO Think about, if this is right
    run_is_private = models.BooleanField(
        default=False,
        blank=False,
        help_text="Whether to show the run and it results publicly.",
    )
    date_created = models.DateTimeField(auto_now_add=True, blank=False)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self) -> str:
        return f"Run {self.pk} {self.workflow} {self.target}"

    @property
    def Messages(self):
        return self.runmessage_set.all().order_by(
            "-snakemake_timestamp"
        )

    @property
    def Status(self):
        return (
            self.runstatus_set.all()
            .order_by("-date_created")
            .first()
            .get_status_display()
        )

    @property
    def MessageHeaders(self):
        headers=defaultdict(int)
        for msg in self.runmessage_set.all().order_by("-snakemake_timestamp"):
            for key, _ in msg.message.items():
                headers[key] += 1
        return headers


def input_data_path(instance, filename):
    settings = WorkflowSetting.objects.get(workflow_id=instance.run.workflow.id)
    return f"{settings.storage_location}/data/{filename}"


class RunInputFile(models.Model):
    """
    Contains all input files for a certain run.
    """

    run = ForeignKey(Run, on_delete=models.CASCADE)
    input_data = models.FileField(
        upload_to=input_data_path,
        blank=False,
        max_length=200,
        storage=OverwriteStorage(),
        help_text="Required. The input data for your run.",
    )

    def __str__(self) -> str:
        filename = os.path.basename(str(self.input_data))
        return f"{self.run}-{filename}"


class RunMessage(models.Model):
    """
    Snakemake output of a certain run.
    """

    run = ForeignKey(Run, on_delete=models.CASCADE)
    message = models.JSONField(blank=False)
    snakemake_timestamp = models.DateTimeField(blank=False)
    date_created = models.DateTimeField(auto_now_add=True, blank=False)

    def __str__(self) -> str:
        return f"{self.run} {self.snakemake_timestamp}"

class RunStatus(models.Model):
    """
    Status of a run.
    """

    run = ForeignKey(Run, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=15, choices=RUN_STATUS_CHOICES, default="CREATED", blank=False
    )
    progress = PositiveSmallIntegerField(default=0, blank=False)
    date_created = models.DateTimeField(auto_now_add=True, blank=False)

    def __str__(self) -> str:
        return f"{self.run} {self.status}"


class Result(models.Model):
    """
    Results of a run.
    """

    run = ForeignKey(Run, on_delete=models.CASCADE)
    path_results = models.FilePathField(
        path=results_path, allow_files=False, allow_folders=True
    )
    path_index_report = models.FilePathField(
        path=results_path, allow_files=True, allow_folders=False
    )
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.path_index_report
