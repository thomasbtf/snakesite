# Generated by Django 3.2.2 on 2021-05-21 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("workflow", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="run",
            name="args",
            field=models.CharField(
                blank=True,
                default="--use-conda",
                help_text="Snakemake command line options to start the run with.",
                max_length=200,
            ),
        ),
        migrations.AlterField(
            model_name="run",
            name="environment_variable",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Environment variable(s), that are exported before the run starts. Format: {'foo' : 'bar', ...}",
                max_length=200,
            ),
        ),
        migrations.AlterField(
            model_name="runstatus",
            name="status",
            field=models.CharField(
                choices=[
                    ("CREATED", "Created"),
                    ("QUEUED", "Queued"),
                    ("TESTING", "Testing"),
                    ("RUNNING", "Running"),
                    ("REPORTING", "Generate Report"),
                    ("FINISHED", "Finished"),
                    ("FAILED", "Failed"),
                ],
                default="CREATED",
                max_length=15,
            ),
        ),
    ]