import os
from re import template
from shutil import rmtree, copytree

import git
from django.conf import settings
from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver

from .models import (RunStatus, Workflow, WorkflowSetting, WorkflowStatus, WorkflowTemplate,
                     WorkflowTemplateSetting)
from .tasks import start_snakemake_run
from .utils import find_file, make_dir


@receiver(post_save, sender=WorkflowTemplate)
def workflow_template_created(sender, instance, created, raw, **kwargs):
    """Creates a template settings, whenever a new workflow template is registered.
    Also downloads the template from GitHub.

    Args:
        sender: The model class.
        instance: The actual instance being saved.
        created (boolean): True if a new record was created.
        raw (boolean): True if the model is saved exactly as presented (i.e. when loading a fixture).
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
def workflow_template_deleted(sender, instance , **kwargs):
    """Deletes a a workflow template and deletes the local workflow copy.

    Args:
        sender: The model class.
        instance: The actual instance being deleted.
    """
    settings = WorkflowTemplateSetting.objects.get(workflow_template_id=instance.pk)
    storage_location = settings.storage_location
    rmtree(storage_location)
    settings.delete()


@receiver(post_save, sender=Workflow)
def workflow_created(sender, instance, created, raw, **kwargs):
    if created:
        storage_location = os.path.join(settings.WORKFLOWS, str(instance.pk))
        template_settings = WorkflowTemplateSetting.objects.get(workflow_template_id=instance.workflow_template.pk)
        template_storage_location = template_settings.storage_location
        copytree(template_storage_location, storage_location)

        WorkflowSetting.objects.create(
            workflow = instance,
            storage_location = storage_location,
            path_snakefile = template_settings.path_snakefile,
            path_sample_sheet = template_settings.path_sample_sheet,
            path_config = template_settings.path_config,
         )

        WorkflowStatus.objects.create(
            workflow=instance
        )

@receiver(pre_delete, sender=Workflow)
def workflow_template_deleted(sender, instance , **kwargs):
    settings = WorkflowSetting.objects.get(workflow_id=instance.pk)
    status = WorkflowStatus.objects.get(workflow_id=instance.pk)
    storage_location = settings.storage_location

    print(storage_location)

    rmtree(storage_location)
    settings.delete()
    status.delete()

# @receiver(post_save, sender=Run)
def create_run_status(sender, instance, created, raw, **kwargs):
    """Creates a new run status, whenever a new run is created.

    Args:
        sender: The model class.
        instance: The actual instance being saved.
        created (boolean): True if a new record was created.
        raw (boolean): True if the model is saved exactly as presented (i.e. when loading a fixture).
    """
    if created:
        RunStatus.objects.create(
            run=instance
        )


# @receiver(post_save, sender=RunStatus)
def start_run(sender, instance, created, raw, **kwargs):
    if instance.status == "QUEUED":
        start_snakemake_run(instance.pk)
