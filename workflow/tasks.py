import os
import shlex

from celery import shared_task, chain

from .models import Run, WorkflowSetting
from .utils import CommandRunner


def start_snakemake_run(run_pk: int):
    run_instance = Run.objects.get(pk=run_pk)
    worklow_setting_instance = WorkflowSetting.objects.get(workflow=run_instance.workflow)

    cores = run_instance.cores
    workdir = worklow_setting_instance.storage_location
    snakefile = os.path.join(workdir, worklow_setting_instance.path_snakefile)
    target = run_instance.target

    args = f"snakemake --use-conda --snakefile '{snakefile}' --cores {cores} --directory '{workdir}' {target}"

    chain(snakemake_dry_run.si(args), snakemake_run.si(args), snakemake_report.si(args)).apply_async()


@shared_task
def snakemake_dry_run(args):
    runner = CommandRunner()
    args += " -npr"
    args = shlex.split(args)
    runner.run_command(args)
    return "Dry-Run Done"


@shared_task
def snakemake_run(args):
    runner = CommandRunner()
    args = shlex.split(args)
    runner.run_command(args)
    return "Run Done"


@shared_task
def snakemake_report(args):
    return "Report Done"