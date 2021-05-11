import os

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields import PositiveSmallIntegerField
from django.db.models.fields.related import ForeignKey


WORKFLOW_STATUS_CHOICES = [
    ("CREATED", "Created"),
    ("TESTING", "Testing"),
    ("RUNNING", "Running"),
    ("PRODUCTION", "Available"),
    ("DEPRECATED", "Deprecated"),
]

RUN_STATUS_CHOICES = [
    ("QUEUED", "Queued"),
    ("RUNNING", "Running"),
    ("FAILED","Failed"),
    ("SUCCESSFULL", "Successful"),
]

def workflows_path():
    return os.path.join(settings.BASE_DIR, 'workflows')

def results_path():
    return os.path.join(settings.BASE_DIR, 'results')

class WorkflowRegistry(models.Model):
    name = models.CharField(max_length=60, blank=False)
    description = models.TextField(max_length=400, blank=False)
    url = models.URLField(blank=False)
    owner = models.ManyToManyField(User, blank=False, related_name="workflow_owner")
    contributors = models.ManyToManyField(User, blank=True, related_name="workflow_contributors")
    date_created = models.DateTimeField(auto_now_add=True, blank=False)
    date_modified = models.DateTimeField(auto_now=True, blank=False)

    def __str__(self) -> str:
        return self.name

class Workflow(models.Model):
    registration = models.ForeignKey(WorkflowRegistry, on_delete=models.CASCADE)
    version = models.PositiveSmallIntegerField(default=1, blank=False)
    storage_location = models.FilePathField(path=workflows_path, allow_files= False, allow_folders=True, blank=False)
    path_snakefile = models.FilePathField(path=workflows_path, allow_files= True, allow_folders=False, blank=False)
    path_config = models.FilePathField(path=workflows_path, allow_files= True, allow_folders=False, blank=False)
    path_sample_sheet = models.FilePathField(path=workflows_path, allow_files= True, allow_folders=False, blank=False)
    date_created = models.DateTimeField(auto_now_add=True, blank=False)

    def __str__(self) -> str:
        return f"{self.registration}-{self.version}"

class WorkflowStatus(models.Model):
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE)
    status = models.CharField(max_length=15, choices=WORKFLOW_STATUS_CHOICES, default="CREATED", blank=False)
    date_created = models.DateTimeField(auto_now_add=True, blank=False)

    def __str__(self) -> str:
        return self.status

class Run(models.Model):
    workflow = ForeignKey(Workflow, on_delete=models.CASCADE)
    created_by = ForeignKey(User, on_delete=models.SET_NULL, null=True)
    input_data = models.FileField(blank=False)
    sample_sheet = models.FileField(blank=False)
    config = models.FileField(blank=False)
    target = models.CharField(max_length=30, default="all", blank=False)
    cores = models.PositiveSmallIntegerField(default=1, blank=False)
    result_is_private = models.BooleanField(default=False, blank=False)
    date_created = models.DateTimeField(auto_now_add=True, blank=False)

    def __str__(self) -> str:
        return f"{self.workflow}-{self.target}"

class RunMessage(models.Model):
    run = ForeignKey(Run, on_delete=models.CASCADE)
    level= models.CharField(max_length=30, default="test", blank=False)
    job = models.CharField(max_length=100, default="test", blank=False)
    message = models.TextField(max_length=100, default="test", blank=False)
    date_created = models.DateTimeField(auto_now_add=True, blank=False)

    def __str__(self) -> str:
        return self.message

class RunStatus(models.Model):
    run = ForeignKey(Run, on_delete=models.CASCADE)
    status =  models.CharField(max_length=15,choices=RUN_STATUS_CHOICES, default="QUEUED", blank=False)
    progress = PositiveSmallIntegerField(default=0, blank=False)
    date_created = models.DateTimeField(auto_now_add=True, blank=False)

    def __str__(self) -> str:
        return self.status

class Result(models.Model):
    run = ForeignKey(Run, on_delete=models.CASCADE)
    path_results = models.FilePathField(path=results_path, allow_files= False, allow_folders=True)
    path_index_report = models.FilePathField(path=results_path, allow_files= True, allow_folders=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.path_index_report
