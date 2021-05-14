from rest_framework import generics

from workflow.models import Workflow, Run, Result
from .serializers import WorkflowTemplateSerializer, RunSerializer, ResultSerializer


class WorkflowTemplateView(generics.ListCreateAPIView):
    queryset = Workflow.objects.all()
    serializer_class = WorkflowTemplateSerializer


class RunView(generics.ListCreateAPIView):
    queryset = Run.objects.all()
    serializer_class = RunSerializer


class ResultView(generics.ListAPIView):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer