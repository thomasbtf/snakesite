from rest_framework import serializers
from workflow.models import WorkflowTemplate, Run, Result

class WorkflowTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowTemplate
        fields = ("name", "description", "url", "owner", "contributors", "version")

class RunSerializer(serializers.ModelSerializer):
    class Meta:
        model = Run
        fields = ("workflow", "created_by", "sample_sheet", "config", "target", "cores", "result_is_private")

class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = ("run", "path_results", "path_index_report", "date_created")