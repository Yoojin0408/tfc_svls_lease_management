import json
import os
import requests
import re
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities import parameters

logger = Logger()
tracer = Tracer()

def validate_signature(signature_count):
    return True if signature_count > 0 else False

def sanitise_abn(abn):
    return re.sub(r'[^0-9]+', '', abn).strip()

@tracer.capture_method
def validate_abn(entity_name, abn):

    sanitised_abn = sanitise_abn(abn)
    abn_guid = parameters.get_secret("tfc_abn_guid")
    
    url = f'https://abr.business.gov.au/json/AbnDetails.aspx?abn={sanitised_abn}&callback=callback&guid={abn_guid}'

    response = requests.get(url)
    json_str = re.sub(r"^callback\((.*)\)$", r"\1", response.text)

    if response.status_code == 200:

        data = json.loads(json_str)
        if data.get('EntityName') == entity_name:
            return True
        
    return False
              
@logger.inject_lambda_context
@tracer.capture_lambda_handler
def lambda_handler(event, context):
    print(event)

    isValid = False

    isSigned = validate_signature(event['data']['signature_count'])
    isValidAbn = validate_abn(event['data']['Landlord'], event['data']['Landlord ABN'])

    
    isValid = True if isSigned and isValidAbn else False

    return {
        'isValid': isValid
    }
