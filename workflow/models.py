import os

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.fields import PositiveSmallIntegerField
from django.db.models.fields.related import ForeignKey

from .storage import OverwriteStorage
from .utils import make_dir

WORKFLOW_STATUS_CHOICES = [
    ("CREATED", "Created"),
    ("TESTING", "Testing"),
    ("RUNNING", "Running"),
    ("PRODUCTION", "Available"),
    ("DEPRECATED", "Deprecated"),
]

RUN_STATUS_CHOICES = [
    ("CREATED", "Created"),
    ("QUEUED", "Queued"),
    ("RUNNING", "Running"),
    ("FAILED","Failed"),
    ("SUCCESSFULL", "Successful"),
]

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
    name = models.CharField(max_length=60, blank=False)
    description = models.TextField(max_length=400, blank=False)
    url = models.URLField(blank=False)
    owner = models.ManyToManyField(User, blank=False, related_name="workflow_owner")
    contributors = models.ManyToManyField(User, blank=True, related_name="workflow_contributors")
    version = models.PositiveSmallIntegerField(default=1, blank=False)
    date_created = models.DateTimeField(auto_now_add=True, blank=False)
    date_modified = models.DateTimeField(auto_now=True, blank=False)
    
    class Meta:
        unique_together = (('name', 'version'),)

    def __str__(self) -> str:
        return f"{self.name}-{self.version}"

    def get_safe_storage_location(self):
        keepcharacters = ('.','_')
        cleaned = [c.lower() for c in self.name if c.isalnum() or c in keepcharacters]
        return f"{self.pk}-" + "".join(cleaned).rstrip()

class Workflow(models.Model):
    """
    The local copy of a workflow.
    """
    parent_workflow = models.ForeignKey(WorkflowTemplate, on_delete=models.SET_NULL, null=True)
    storage_location = models.FilePathField(path=workflows_path, allow_files= False, allow_folders=True, blank=False)
    path_snakefile = models.CharField(max_length=100, blank=False)
    path_sample_sheet = models.CharField(max_length=100, blank=False)
    path_config = models.CharField(max_length=100, blank=False)
    accessible_by = models.ManyToManyField(User, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, blank=False)

    def __str__(self) -> str:
        return f"{self.parent_workflow.name}-{self.parent_workflow.version}"


class WorkflowStatus(models.Model):
    """
    Represents the status of the local Workflow. Can change over time.
    """
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE)
    status = models.CharField(max_length=15, choices=WORKFLOW_STATUS_CHOICES, default="CREATED", blank=False)
    date_created = models.DateTimeField(auto_now_add=True, blank=False)

    def __str__(self) -> str:
        return f"{self.workflow.__str__()}-{self.status}"


def sample_sheet_path(instance, filename):
    return os.path.join(instance.workflow.storage_location, instance.workflow.path_sample_sheet)

def config_path(instance, filename):
    return os.path.join(instance.workflow.storage_location, instance.workflow.path_config)

class Run(models.Model):
    """
    Represent a run of a certain workflow.
    """
    workflow = ForeignKey(Workflow, on_delete=models.CASCADE)
    created_by = ForeignKey(User, on_delete=models.SET_NULL, null=True)
    sample_sheet = models.FileField(upload_to=sample_sheet_path, blank=False, max_length=200, storage=OverwriteStorage())
    config = models.FileField(upload_to=config_path, max_length=200, storage=OverwriteStorage())
    target = models.CharField(max_length=30, default="all", blank=False)
    cores = models.PositiveSmallIntegerField(default=1, blank=False)
    result_is_private = models.BooleanField(default=False, blank=False)
    date_created = models.DateTimeField(auto_now_add=True, blank=False)

    def __str__(self) -> str:
        return f"Run-{self.pk}-{self.workflow}-{self.target}"


def input_data_path(instance, filename):
    return f"{instance.run.workflow.storage_location}/data/{filename}"  

class InputFile(models.Model):
    """
    Contains all input files for a certain run.
    """
    run = ForeignKey(Run, on_delete=models.CASCADE)
    input_data = models.FileField(upload_to=input_data_path, blank=False, max_length=200, storage=OverwriteStorage())

    def __str__(self) -> str:
        filename = os.path.basename(str(self.input_data))
        return f"{self.run.__str__()}-{filename}"


class RunMessage(models.Model):
    """
    Snakemake stdout of a certain run.
    """
    run = ForeignKey(Run, on_delete=models.CASCADE)
    level= models.CharField(max_length=30, default="test", blank=False)
    job = models.CharField(max_length=100, default="test", blank=False)
    message = models.TextField(max_length=100, default="test", blank=False)
    date_created = models.DateTimeField(auto_now_add=True, blank=False)

    def __str__(self) -> str:
        return self.message


class RunStatus(models.Model):
    """
    Status of a run.
    """
    run = ForeignKey(Run, on_delete=models.CASCADE)
    status =  models.CharField(max_length=15,choices=RUN_STATUS_CHOICES, default="CREATED", blank=False)
    progress = PositiveSmallIntegerField(default=0, blank=False)
    date_created = models.DateTimeField(auto_now_add=True, blank=False)

    def __str__(self) -> str:
        return f"{self.run.__str__()}-{self.status}"


class Result(models.Model):
    """
    Results of a run.
    """
    run = ForeignKey(Run, on_delete=models.CASCADE)
    path_results = models.FilePathField(path=results_path, allow_files= False, allow_folders=True)
    path_index_report = models.FilePathField(path=results_path, allow_files= True, allow_folders=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.path_index_report
