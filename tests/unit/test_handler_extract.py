#  $POWERTOOLS_IDEMPOTENCY_DISABLED=1 python3 -m pytest unit
import json
from dataclasses import dataclass

import pytest
import sys
sys.path.append("..")
from functions.extract_data import app


@pytest.fixture()
def eb_event():
    """ Generates EventBridge Event"""

    return {
        "version": "0",
        "id": "d76ebb39-779b-6501-817e-8ca9efd43234",
        "detail-type": "Object Created",
        "source": "aws.s3",
        "account": "344612134556",
        "time": "2025-02-18T22:17:31Z",
        "region": "ap-southeast-2",
        "resources": ["arn:aws:s3:::tfchomeworkbucket-yoojinc"],
        "detail": {
            "version": "0",
            "bucket": {
                "name": "tfchomeworkbucket-yoojinc"
            },
            "object": {
                "key": "lease-doc-final.png",
                "size": 89716,
                "etag": "a20617d169d9dfb5a35c6c7398539d59",
                "sequencer": "0067B506FB4E9E2775"
            },
            "request-id": "P3H97DMEQJQKQ56B",
            "requester": "344612134556",
            "source-ip-address": "220.233.199.142",
            "reason": "PutObject"
        }
    }

@pytest.fixture
def context():
    """ 
    Context object isn't generated during unit test, failing the test. 
    There is no environment variable to disable @logger.inject_lambda_context
    Generate dummy Context object to bypass @logger.inject_lambda_context
    """
    @dataclass
    class LambdaContext:
        function_name: str = "extract_data_lambda"
        aws_request_id: str = "88888888-4444-4444-4444-121212121212"
        invoked_function_arn: str = "arn:aws:lambda:ap-southeast-2:123456789101:function:test"
        memory_limit_in_mb:int = 128
    return LambdaContext()


def test_lambda_handler(eb_event, context):

    ret = app.lambda_handler(eb_event, context)

    assert ret['bucket'] == 'tfchomeworkbucket-yoojinc'
    assert "Landlord" in ret["data"]
    assert ret["data"]["Landlord"] == "THE TRUSTEE FOR PSS FUND"

