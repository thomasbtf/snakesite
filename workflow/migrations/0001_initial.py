# Generated by Django 3.2.2 on 2021-05-18 21:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import workflow.models
import workflow.storage


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Run',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sample_sheet', models.FileField(help_text='Required. Upload your sample sheet here. Paths to input data files must start with "data/".', max_length=200, storage=workflow.storage.OverwriteStorage(), upload_to=workflow.models.sample_sheet_path)),
                ('config', models.FileField(blank=True, help_text='Optional. Upload a changed config file here. Else the default config from the workflow is used.', max_length=200, storage=workflow.storage.OverwriteStorage(), upload_to=workflow.models.config_path)),
                ('target', models.CharField(default='all', help_text='Target(s) to build by snakemake. May be rules or files.', max_length=30)),
                ('cores', models.PositiveSmallIntegerField(default=6, help_text='Number of maximum CPU cores/jobs running in parallel.')),
                ('run_is_private', models.BooleanField(default=False, help_text='Whether to show the run and it results publicly.')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Workflow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='The name of your workflow. E.g. "SARS-CoV-2 Production".', max_length=60)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('accessible_by', models.ManyToManyField(blank=True, related_name='accessible_by', to=settings.AUTH_USER_MODEL)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='workflow_owner', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='WorkflowTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=60, unique=True)),
                ('description', models.TextField(max_length=400)),
                ('url', models.URLField()),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('contributors', models.ManyToManyField(blank=True, related_name='workflow_template_contributors', to=settings.AUTH_USER_MODEL)),
                ('owner', models.ManyToManyField(related_name='workflow_template_owner', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='WorkflowTemplateSetting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path_snakefile', models.CharField(max_length=100)),
                ('path_sample_sheet', models.CharField(max_length=100)),
                ('path_config', models.CharField(max_length=100)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('storage_location', models.FilePathField(allow_files=False, allow_folders=True, path=workflow.models.templates_path)),
                ('workflow_template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='workflow.workflowtemplate')),
            ],
        ),
        migrations.CreateModel(
            name='WorkflowStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('CREATED', 'Created'), ('TESTING', 'Testing'), ('QUEUED', 'Queued'), ('RUNNING', 'Running'), ('AVAILABLE', 'Available'), ('DEPRECATED', 'Deprecated')], default='CREATED', max_length=15)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('workflow', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='workflow.workflow')),
            ],
        ),
        migrations.CreateModel(
            name='WorkflowSetting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('storage_location', models.FilePathField(allow_files=False, allow_folders=True, path=workflow.models.workflows_path)),
                ('path_snakefile', models.CharField(max_length=100)),
                ('path_sample_sheet', models.CharField(max_length=100)),
                ('path_config', models.CharField(max_length=100)),
                ('workflow', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='workflow.workflow')),
            ],
        ),
        migrations.AddField(
            model_name='workflow',
            name='workflow_template',
            field=models.ForeignKey(help_text='Select the template you want to use.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='workflow.workflowtemplate'),
        ),
        migrations.CreateModel(
            name='RunStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('CREATED', 'Created'), ('QUEUED', 'Queued'), ('RUNNING', 'Running'), ('FAILED', 'Failed'), ('SUCCESSFULL', 'Successful')], default='CREATED', max_length=15)),
                ('progress', models.PositiveSmallIntegerField(default=0)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('run', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='workflow.run')),
            ],
        ),
        migrations.CreateModel(
            name='RunMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.CharField(default='test', max_length=30)),
                ('job', models.CharField(default='test', max_length=100)),
                ('message', models.TextField(default='test', max_length=100)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('run', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='workflow.run')),
            ],
        ),
        migrations.CreateModel(
            name='RunInputFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('input_data', models.FileField(help_text='Required. The input data for your run.', max_length=200, storage=workflow.storage.OverwriteStorage(), upload_to=workflow.models.input_data_path)),
                ('run', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='workflow.run')),
            ],
        ),
        migrations.AddField(
            model_name='run',
            name='workflow',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='workflow.workflow'),
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path_results', models.FilePathField(allow_files=False, allow_folders=True, path=workflow.models.results_path)),
                ('path_index_report', models.FilePathField(path=workflow.models.results_path)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('run', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='workflow.run')),
            ],
        ),
    ]
