""" 
View module for handel snakemakes WMSLogger

Snakemakes docs interpretation:
    A WMS monitor is a workflow management system logger to enable
    monitoring with something like Panoptes. The address corresponds to
    the --wms-monitor argument, and args should be a list of key/value
    pairs with extra arguments to send to identify the workflow. We require
    the logging server to exist and receive creating a workflow to start
    the run, but we don't exit with error if any updates fail, as the
    workflow will already be running and it would not be worth stopping it.

For further information see:
    https://snakemake.readthedocs.io/en/stable/executing/monitoring.html?highlight=wms#monitoring (docs)
    https://snakemake.readthedocs.io/en/stable/_modules/snakemake/logging.html#WMSLogger (implementation)
    https://github.com/panoptes-organization/monitor-schema/blob/main/spec.md
"""

import json
from datetime import datetime

from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from workflow.models import Run, RunMessage


class ServiceInfoView(APIView):
    """
    Indicates a running service.

    Snakemakes interpretation
        Docs:
            Snakemake gets the status of Panoptes [server]. Snakemake continues 
            to run if the status (json['status']) is 'running'. In all other 
            cases snakemake exits with an error message.

            Snakemakes method: GET
            Data: json
        
        Implementation:
            Service Info ensures that the server is running. We exit on error
            if this isn't the case, so the function can be called in init.
        
        Handels:
            (required) "status" == "running" in json
            (required) 200 Response
    """
        
    def get(self, request):


        data = {
            # TODO add more data from https://ga4gh.github.io/workflow-execution-service-schemas/docs/#section/Authorization-and-Authentication
            # TODO replace with actual version
            "status" : "running",
            "version": "0.1.0"
        }

        return Response(data=data, status=200)


class CreateWorkflowView(APIView):
    """
    Registers run with snakemake. 

    Snakemakes interpretation
        Docs:
            Snakemake gets a unique id/name str(uuid.uuid4()) for each workflow 
            triggered.

            Snakemakes method: GET
            Data: json

        Implementation:
            Creating a workflow means pinging the wms server for a new id, or
            if providing an argument for an existing workflow, ensuring that
            it exists and receiving back the same identifier.

        Handels:
            "id" in json
            200 Success
            401 Authorization is required with a WMS_MONITOR_TOKEN in the environment
            403 Permission is denied to endpoint.
            404 The wms endpoint was not found
            500 There was a server error when trying to access endpoint
            Other The endpoints response code is not recognized.
    """

    def get(self, request):
        # run was already created, and run_id should be in request
        run_pk = request.GET.get("run_id")
        if run_pk:
            run_instance = get_object_or_404(Run, pk=run_pk)

            # "id" is the id from snakemake
            data = {"id": run_instance.uuid}
            return Response(data=data, status=200)

        # run was not found
        # TODO maybe create a new run. but make this sense?
        return Response(status=401)
        

class UpdateWorkflowStatusView(APIView):
    """
    Saves run status to db.

    Snakemakes interpretation
        Docs:
            Snakemake posts updates for workflows/jobs. The dictionary sent contains the log 
            message dictionary, the current timestamp and the unique id/name of the workflow.

            Snakemakes method: POST
            Data: dictionary

            {
                # the log message dictionary
                'msg': repr(msg), 
                'timestamp': time.asctime(),
                'id': id
            }

        Implementation:
            Sends the [snakemake] log to the server.

        Handels:
            200 Success
            401 Authorization is required with a WMS_MONITOR_TOKEN in the environment
            403 Permission is denied to endpoint.
            404 The wms endpoint was not found
            500 There was a server error when trying to access endpoint
            Other The endpoints response code is not recognized.
    """

    def post(self, request):
        run_instance = get_object_or_404(Run, uuid=request.POST.get("id"))
        RunMessage.objects.create(
            run = run_instance,
            message = json.loads(request.POST.get("msg", {})),
            snakemake_timestamp = datetime.strptime(request.POST.get("timestamp"), "%a %b %d %H:%M:%S %Y")
        )
        return Response(status=200)
