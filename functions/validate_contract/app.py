import json
from aws_lambda_powertools import Logger, Tracer

logger = Logger()
tracer = Tracer()

@logger.inject_lambda_context
@tracer.capture_lambda_handler
def lambda_handler(event, context):
    print(event)

    isValid = True
    form_data = event['data']

    required_fields = ['property', 'landlord', 'tenant', 'lease term']
    for field in required_fields:
        if not any(k.lower() == field.lower() for k in form_data):
            isValid = False

    return {
        'isValid': isValid
    }
