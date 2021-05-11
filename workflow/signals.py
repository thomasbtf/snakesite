import os

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from .models import WorkflowRegistry, Workflow, WorkflowStatus, Run, RunStatus
from .utils import make_dir, find_file

import git

@receiver(post_save, sender=WorkflowRegistry)
def create_workflow(sender, instance, created, raw, **kwargs):
    """Creates a new local workflow, whenever a new workflow is registered.

    Args:
        sender: The model class.
        instance: The actual instance being saved.
        created (boolean): True if a new record was created.
        raw (boolean): True if the model is saved exactly as presented (i.e. when loading a fixture).
        """

    if created:
        # TODO find a nicer solution for the folder name changes
        # maybe add it to the model
        storage_location = os.path.join(settings.WORKFLOWS, instance.__str__())
        make_dir(storage_location)

        # TODO think about large repositories and how to handel them
        git.Repo.clone_from(instance.url, storage_location)

        # TODO think about nicer path suggestion algorithm
        snakefile = find_file(storage_location, "Snakefile")
        config = find_file(storage_location, "config.yaml")
        sample_sheet = find_file(storage_location, "samples.csv")

        Workflow.objects.create(
            parent_workflow=instance,
            storage_location=storage_location,
            path_snakefile=snakefile,
            path_config=config,
            path_sample_sheet=sample_sheet,
        )


@receiver(post_save, sender=Workflow)
def create_workflow_status(sender, instance, created, raw, **kwargs):
    """Creates a new workflow status, whenever a new workflow is created.

    Args:
        sender: The model class.
        instance: The actual instance being saved.
        created (boolean): True if a new record was created.
        raw (boolean): True if the model is saved exactly as presented (i.e. when loading a fixture).
    """
    if created:
        WorkflowStatus.objects.create(
            workflow=instance
        )


@receiver(post_save, sender=Run)
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
