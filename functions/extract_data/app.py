import boto3
import json
import time
import re
import uuid
import os
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.idempotency import (
    DynamoDBPersistenceLayer,
    idempotent,
) 

persistence_layer = DynamoDBPersistenceLayer(table_name=os.environ.get('idempotency_table'))

logger = Logger()
tracer = Tracer()

# Create client
textract_client = boto3.client('textract')

def sanitise_key(key):
    return re.sub(r'^\d+\.\s*|[^\w\s]', '', key).strip()

@tracer.capture_method
def extract_form_data(bucket_name, object_key): # Calls Textract AnalyzeDocument API

    response = textract_client.analyze_document(
        Document={"S3Object": {"Bucket": bucket_name, "Name": object_key}},
        FeatureTypes=["FORMS", "SIGNATURES"],
    )

    # Extract key-value pairs
    key_map = {}
    value_map = {}
    block_map = {}
    signature_count = 0

    for block in response["Blocks"]:
        block_map[block["Id"]] = block
        if block["BlockType"] == "KEY_VALUE_SET":
            if "EntityTypes" in block and "KEY" in block["EntityTypes"]:
                key_map[block["Id"]] = block
            if "EntityTypes" in block and "VALUE" in block["EntityTypes"]:
                value_map[block["Id"]] = block
        elif block["BlockType"] == "SIGNATURE":
            signature_count += 1
            
    # Find key-value pairs
    form_data = {"ID": str(uuid.uuid4())}
    for key_id, key_block in key_map.items():
        key_text = sanitise_key(get_text(key_block, block_map))
        value_block = find_value_block(key_block, value_map)
        value_text = get_text(value_block, block_map) if value_block else "N/A"
        form_data[key_text] = value_text

    form_data["signature_count"] = signature_count  

    return form_data

def get_text(block, block_map): # Extracts text from a Textract block

    text = ""

    if "Relationships" in block:
        for relationship in block["Relationships"]:
            if relationship["Type"] == "CHILD":
                for child_id in relationship["Ids"]:
                    word_block = block_map[child_id]
                    if word_block["BlockType"] == "WORD":
                        text += word_block["Text"] + " "
    return text.strip()

def find_value_block(key_block, value_map): # Finds the corresponding value block for a given key block

    if "Relationships" in key_block:
        for relationship in key_block["Relationships"]:
            if relationship["Type"] == "VALUE":
                for value_id in relationship["Ids"]:
                    return value_map.get(value_id)
    return None

@logger.inject_lambda_context
@tracer.capture_lambda_handler
@idempotent(persistence_store=persistence_layer)
def lambda_handler(event, context):
    print(event)

    # Get the S3 bucket name and object key from the event
    bucket_name = event['detail']['bucket']['name']
    object_key = event['detail']['object']['key']
    
    logger.info(f'Received S3 event: Bucket={bucket_name}, Object={object_key}')

    response = None  

    try:
        # Extract data using Textract
        form_data = extract_form_data(bucket_name, object_key)

        print(json.dumps(form_data))

    except Exception as e:
        logger.exception("An unexpected error occurred", log=e)
        raise Exception(e)

    # Start the Step Function execution and pass the S3 bucket name and object key as input
    response = {
        'bucket': bucket_name,
        'key': object_key,
        'data': form_data
    }

    return response