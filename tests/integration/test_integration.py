# $POWERTOOLS_IDEMPOTENCY_DISABLED=1 DOCKER_HOST=unix://$HOME/.docker/run/docker.sock sam local invoke --event events/extract_data_event.json "TfcExtractDataFunction" --region ap-southeast-2

# Integration test:
# DOCKER_HOST=unix://$HOME/.docker/run/docker.sock sam local start-lambda --region ap-southeast-2        
# POWERTOOLS_IDEMPOTENCY_DISABLED=1 python3 -m pytest integration
# AWS_SAM_STACK_NAME=lease-verification-service python3 -m pytest -s tests/integration -v


import os
import json
import boto3
import botocore
import pytest

# """
# Make sure env variable AWS_SAM_STACK_NAME exists with the name of the stack we are going to test. 
# """


class TestApiGateway:

    @pytest.fixture()
    def lambda_function_output(self):
        """ Get the API Gateway URL from Cloudformation Stack outputs """
        stack_name = os.environ.get("AWS_SAM_STACK_NAME")

        if stack_name is None:
            raise ValueError('Please set the AWS_SAM_STACK_NAME environment variable to the name of your stack')

        client = boto3.client("cloudformation")

        try:
            response = client.describe_stacks(StackName=stack_name)
        except Exception as e:
            raise Exception(
                f"Cannot find stack {stack_name} \n" f'Please make sure a stack with the name "{stack_name}" exists'
            ) from e

        stacks = response["Stacks"]
        stack_outputs = stacks[0]["Outputs"]
        function_output = [output for output in stack_outputs if output["OutputKey"] == "TfcExtractDataFunction"]

        if not function_output:
            raise KeyError(f"TfcExtractDataFunction not found in stack {stack_name}")

        return function_output[0]["OutputValue"]  # Extract url from stack outputs
    
    def test_function(self, lambda_function_output):

        lambda_client = boto3.client('lambda')

        response = lambda_client.invoke(FunctionName=lambda_function_output)
        status_code = response['StatusCode']

        assert status_code == 200