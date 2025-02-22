import json
import pytest
import sys
import os
from dataclasses import dataclass

sys.path.append("..")
from functions.validate_compliance import app

@pytest.fixture
def context():
    """ 
    Context object isn't generated during unit test, failing the test. 
    There is no environment variable to disable @logger.inject_lambda_context
    Generate dummy Context object to bypass @logger.inject_lambda_context
    """
    @dataclass
    class LambdaContext:
        function_name: str = "validate_compliance_lambda"
        aws_request_id: str = "88888888-4444-4444-4444-121212121212"
        invoked_function_arn: str = "arn:aws:lambda:ap-southeast-2:123456789101:function:test"
        memory_limit_in_mb:int = 128
    return LambdaContext()

@pytest.fixture()
def sfn_event_pass():
    """ Generates state machine input"""

    return {
        "bucket": "tfchomeworkbucket-yoojinc",
        "key": "lease-doc-final.png",
        "data": {
            "ID": "cf1f6f86-ec4b-41a3-930d-054181a41400",
            "Tenant ABN": "98 765 432 109",
            "Tenant": "XYZ Enterprises Pty Ltd",
            "Landlord ABN": "74 172 177 893",
            "Property": "The premises located at 123 Commercial Street, Sydney, NSW, 2000",
            "Landlord": "THE TRUSTEE FOR PSS FUND",
            "Termination  Renewal": "The tenant may renew the lease for an additional 5-year term upon mutual agreement. Termination requires a 3-month notice from either party.",
            "Date": "20/02/2025",
            "Maintenance  Repairs": "The tenant is responsible for internal repairs, while the landlord is responsible for structural maintenance.",
            "Lease Term": "The lease commences on 1st March 2025 and continues for a period of 5 years.",
            "Page": "1",
            "Rent  Payments": "The tenant agrees to pay a monthly rent of AUD 5,000, payable on the 1st day of each month.",
            "signature_count": 1
        }
    }

@pytest.fixture()
def sfn_event_fail():
    """ Generates state machine input"""

    return {
        "bucket": "tfchomeworkbucket-yoojinc",
        "key": "lease-doc-final.png",
        "data": {
            "ID": "cf1f6f86-ec4b-41a3-930d-054181a41400",
            "Tenant ABN": "98 765 432 109",
            "Tenant": "XYZ Enterprises Pty Ltd",
            "Landlord": "THE TRUSTEE FOR PSS FUNDS",
            "Landlord ABN": "74 172 177 8934",
            "Property": "The premises located at 123 Commercial Street, Sydney, NSW, 2000",
            "Termination  Renewal": "The tenant may renew the lease for an additional 5-year term upon mutual agreement. Termination requires a 3-month notice from either party.",
            "Date": "20/02/2025",
            "Maintenance  Repairs": "The tenant is responsible for internal repairs, while the landlord is responsible for structural maintenance.",
            "Lease Term": "The lease commences on 1st March 2025 and continues for a period of 5 years.",
            "Page": "1",
            "Rent  Payments": "The tenant agrees to pay a monthly rent of AUD 5,000, payable on the 1st day of each month.",
            "signature_count": 1
        }
    }

def test_lambda_handler_pass(sfn_event_pass, context):

    ret = app.lambda_handler(sfn_event_pass, context)

    assert ret['isValid'] == True

def test_lambda_handler_fail(sfn_event_fail, context):

    ret = app.lambda_handler(sfn_event_fail, context)

    assert ret['isValid'] == False
