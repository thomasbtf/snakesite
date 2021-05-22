import os
from shutil import copytree, rmtree

import git
from django.conf import settings
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from .models import (
    Run,
    RunMessage,
    RunStatus,
    Workflow,
    WorkflowSetting,
    WorkflowStatus,
    WorkflowTemplate,
    WorkflowTemplateSetting,
)
from .tasks import start_snakemake_run
from .utils import broadcast_message, find_file, make_dir


@receiver(post_save, sender=WorkflowTemplate)
def workflow_template_created(sender, instance, created, raw, **kwargs):
    """
    Creates a template setting, whenever a new workflow template is registered.
    Also downloads the template from GitHub.
    """

    if created:
        # TODO find a nicer solution for the folder name changes
        # maybe add it to the model
        storage_location = os.path.join(settings.WORKFLOW_TEMPLATES, str(instance.pk))
        make_dir(storage_location)

        # TODO think about large repositories and how to handel them
        git.Repo.clone_from(instance.url, storage_location)

        # TODO think about nicer path suggestion algorithm
        snakefile = find_file(storage_location, "Snakefile")
        config = find_file(storage_location, "config.yaml")
        sample_sheet = find_file(storage_location, "samples.csv")

        WorkflowTemplateSetting.objects.create(
            workflow_template=instance,
            storage_location=storage_location,
            path_snakefile=snakefile,
            path_sample_sheet=sample_sheet,
            path_config=config,
        )


@receiver(pre_delete, sender=WorkflowTemplate)
def workflow_template_deleted(sender, instance, **kwargs):
    """
    Deletes the local template workflow copy, if template is deleted.
    """
    settings = WorkflowTemplateSetting.objects.get(workflow_template_id=instance.pk)
    storage_location = settings.storage_location
    rmtree(storage_location)


@receiver(post_save, sender=Workflow)
def workflow_created(sender, instance, created, raw, **kwargs):
    if created:
        storage_location = os.path.join(settings.WORKFLOWS, str(instance.pk))
        template_settings = WorkflowTemplateSetting.objects.get(
            workflow_template_id=instance.workflow_template.pk
        )
        template_storage_location = template_settings.storage_location
        copytree(template_storage_location, storage_location)

        WorkflowSetting.objects.create(
            workflow=instance,
            storage_location=storage_location,
            path_snakefile=template_settings.path_snakefile,
            path_sample_sheet=template_settings.path_sample_sheet,
            path_config=template_settings.path_config,
        )

        WorkflowStatus.objects.create(workflow=instance)


@receiver(pre_delete, sender=Workflow)
def workflow_deleted(sender, instance, **kwargs):
    """
    Deleted the local representation of the workflow, when the workflow is deleted.
    """
    rmtree(WorkflowSetting.objects.get(workflow_id=instance.pk).storage_location)


@receiver(post_save, sender=Run)
def run_created(sender, instance, created, raw, **kwargs):
    """
    Creates a new run status, whenever a run is created.
    """
    if created:
        RunStatus.objects.create(run=instance)
        start_snakemake_run(instance.pk)


@receiver(pre_delete, sender=Run)
def run_deleted(sender, instance, **kwargs):
    """
    When a run is deleted, this frees up the workflow.
    """
    WorkflowStatus.objects.create(
        workflow=Workflow.objects.get(pk=instance.workflow.pk),
        status="AVAILABLE",
    )


@receiver(post_save, sender=RunMessage)
def runmessages_created(sender, instance, created, raw, **kwargs):
    """
    When a run message is created, this updates the message table
    """
    if created:
        group_name = str(instance.run.id)
        msg = [
            {"timestamp": instance.snakemake_timestamp.strftime("%H:%M:%S")},
            instance.message,
        ]
        broadcast_message(msg, group_name)


@receiver(post_save, sender=RunStatus)
def runstatus_created(sender, instance, created, raw, **kwargs):
    """
    When a run status is created, this updates the frontend
    """
    if created:
        group_name = "".join(["status_", str(instance.run.id)])
        msg = [{"run_status": instance.get_status_display()}]
        broadcast_message(msg, group_name)
