import ast
import os
import shlex
import zipfile

from celery import chain, shared_task
from django.conf import settings

from .models import Result, Run, RunStatus, WorkflowSetting, WorkflowStatus
from .utils import CommandRunner, make_dir


def set_run_status(run_pk: int, status: str):
    """
    Helper function to set status of run.

    Args:
        run_pk (int): Primary key of run
        status (str): Status of run to set
    """
    RunStatus.objects.create(run=Run.objects.get(pk=run_pk), status=status)


def set_workflow_status(run_pk: int, status: str):
    """
    Helper function to set status of workflow.

    Args:
        run_pk (int): Primary key of run
        status (str): Status of run to set
    """
    WorkflowStatus.objects.create(
        workflow=Run.objects.get(pk=run_pk).workflow, status=status
    )


def cancel_run(self, run_pk):
    """Helper function to set failed run.

    Args:
        run_pk (int): Primary key of run
    """
    set_run_status(run_pk, "FAILED")
    set_workflow_status(run_pk, "AVAILABLE")
    self.request.chain = None


def start_snakemake_run(run_pk: int) -> None:
    """
    Starts snakemake run pipeline: dry-run -> run -> report

    Args:
        run_pk (int): Primary key of run

    Raises:
        ValueError: Illegal values in args user input
    """
    set_run_status(run_pk, "QUEUED")

    run_instance = Run.objects.get(pk=run_pk)
    worklow_setting_instance = WorkflowSetting.objects.get(
        workflow=run_instance.workflow
    )

    cores = run_instance.cores
    workdir = worklow_setting_instance.storage_location
    snakefile = os.path.join(workdir, worklow_setting_instance.path_snakefile)
    target = run_instance.target
    args = shlex.split(run_instance.args)
    if run_instance.environment_variable:
        env_vars = ast.literal_eval(run_instance.environment_variable)
    else:
        env_vars = {}

    # TODO add more validation of user input
    not_to_use_cli_args = [
        "--snakefile",
        "--cores",
        "--directory",
        "---wms-monitor",
        "--wms-monitor-arg",
    ]

    illegal_values = [illegal for illegal in args if illegal in not_to_use_cli_args]
    if illegal_values:
        raise ValueError(
            "Please do use the following cli argument(s): {}".format(illegal_values)
        )

    args = (
        f"snakemake --wms-monitor http://127.0.0.1:8000/api --wms-monitor-arg run_id={run_instance.id} ",
        f"workflow_id={run_instance.workflow_id} --snakefile '{snakefile}' --cores {cores} ",
        f"--directory '{workdir}' --use-conda {target}",
    )

    args = "".join(args)

    results_dir = os.path.join(settings.RESULTS, str(run_instance.workflow_id), str(run_pk))
    report_name = "{date}-workflow-{wf_pk}-run-{run_pk}.zip".format(
        date=run_instance.date_created.strftime("%Y-%m-%d"),
        run_pk=run_pk,
        wf_pk=run_instance.workflow_id,
    )

    chain(
        snakemake_dry_run.si(run_pk, args, env_vars),
        snakemake_run.si(run_pk, args, env_vars),
        snakemake_report.si(run_pk, args, env_vars, results_dir, report_name),
        success.si(run_pk),
    ).apply_async()


@shared_task(bind=True)
def snakemake_dry_run(self, run_pk: int, args: str, env_vars: dict) -> int:
    """Starts a snakemake dry run.

    Args:
        run_pk (int): Primary key of run
        args (str): Arguments to snakemake with
        env_vars (dict): Environment variabels

    Returns:
        int: Returncode of snakemake execution
    """
    try:
        set_run_status(run_pk, "TESTING")
        set_workflow_status(run_pk, "RUNNING")

        args += " -npr"
        args = shlex.split(args)
        runner = CommandRunner()
        runner.run_command(cmd=args, env=env_vars)

        if runner.retval == 1:
            cancel_run(self, run_pk)

        return runner.retval

    except:  # noqa: E722
        cancel_run(self, run_pk)


@shared_task(bind=True)
def snakemake_run(self, run_pk: int, args: str, env_vars: dict) -> int:
    """Starts a snakemake run.

    Args:
        run_pk (int): Primary key of run
        args (str): Arguments to snakemake with
        env_vars (dict): Environment variabels

    Returns:
        int: Returncode of snakemake execution
    """
    try:
        set_run_status(run_pk, "RUNNING")

        args = shlex.split(args)
        runner = CommandRunner()
        runner.run_command(args, env=env_vars)

        if runner.retval == 1:
            cancel_run(self, run_pk)

        return runner.retval

    except:  # noqa: E722
        cancel_run(self, run_pk)


@shared_task(bind=True)
def snakemake_report(
    self, run_pk: int, args: str, env_vars: dict, results_dir: str, report_name: str
) -> int:
    """Generates snakemake report.

    Args:
        run_pk (int): Primary key of run
        args (str): Arguments to snakemake with
        env_vars (dict): Environment variabels
        results_dir (str): path to result zip
        report_name (str): Arguments to snakemake with

    Returns:
        int: Returncode of snakemake execution
    """
    try:
        set_run_status(run_pk, "REPORTING")

        make_dir(results_dir)
        report_path = os.path.join(results_dir, report_name)

        args += f" --report {report_path}"
        args = shlex.split(args)
        runner = CommandRunner()
        runner.run_command(args, env=env_vars)

        if runner.retval == 1:
            cancel_run(self, run_pk)

        with zipfile.ZipFile(report_path, "r") as zip_ref:
            zip_ref.extractall(results_dir)

        Result.objects.create(
            run=Run.objects.get(pk=run_pk),
            path_results=results_dir,
            path_result_zip=report_path,
            path_index_report=os.path.join(
                results_dir, report_name.removesuffix(".zip"), "report.html"
            ),
        )

        return runner.retval

    except:  # noqa: E722
        cancel_run(self, run_pk)


@shared_task()
def success(run_pk: int) -> None:
    """
    Frees up workflow and run.

    Args:
        run_pk (int): Primary key of run
    """
    set_run_status(run_pk, "FINISHED")
    set_workflow_status(run_pk, "AVAILABLE")
