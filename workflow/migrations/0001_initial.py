# Generated by Django 3.2.2 on 2021-05-11 11:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import workflow.models


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
                ('input_data', models.FileField(upload_to='')),
                ('sample_sheet', models.FileField(upload_to='')),
                ('config', models.FileField(upload_to='')),
                ('target', models.CharField(default='all', max_length=30)),
                ('cores', models.PositiveSmallIntegerField(default=1)),
                ('result_is_private', models.BooleanField(default=False)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Workflow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.PositiveSmallIntegerField(default=1)),
                ('storage_location', models.FilePathField(allow_files=False, allow_folders=True, path=workflow.models.workflows_path)),
                ('path_snakefile', models.FilePathField(path=workflow.models.workflows_path)),
                ('path_config', models.FilePathField(path=workflow.models.workflows_path)),
                ('path_sample_sheet', models.FilePathField(path=workflow.models.workflows_path)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='WorkflowStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('CREATED', 'Created'), ('TESTING', 'Testing'), ('RUNNING', 'Running'), ('PRODUCTION', 'Available'), ('DEPRECATED', 'Deprecated')], default='CREATED', max_length=15)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('workflow', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='workflow.workflow')),
            ],
        ),
        migrations.CreateModel(
            name='WorkflowRegistry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=60)),
                ('description', models.TextField(max_length=400)),
                ('url', models.URLField()),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('contributors', models.ManyToManyField(blank=True, related_name='workflow_contributors', to=settings.AUTH_USER_MODEL)),
                ('owner', models.ManyToManyField(related_name='workflow_owner', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='workflow',
            name='registration',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='workflow.workflowregistry'),
        ),
        migrations.CreateModel(
            name='RunStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('QUEUED', 'Queued'), ('RUNNING', 'Running'), ('FAILED', 'Failed'), ('SUCCESSFULL', 'Successful')], default='QUEUED', max_length=15)),
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