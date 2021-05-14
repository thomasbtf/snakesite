import os
import shlex
import subprocess

from .models import Run


def start_snakemake_run(run_pk: int):
    instance = Run.objects.get(pk=run_pk)

    cores = instance.cores
    workdir = instance.workflow.storage_location
    snakefile = os.path.join(workdir, instance.workflow.path_snakefile)
    target = instance.target


    args = f"snakemake --use-conda --snakefile '{snakefile}' --cores {cores} --directory '{workdir}' {target}"
    args = shlex.split(args)
    subprocess.Popen(args)
