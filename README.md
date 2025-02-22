# lease-verification-service

The example appplication is based on commercial lease management domain, primarily for retail customers. Customer signs a new commercial lease agreement and uploads the document to manage and analyse the data. The example is an event based serverless architecture that uses Lambda, Step Functions, SQS, SNS, S3, DynamoDB services. 

![architecture](../architecture/architecture.png)

1. User uploads lease document (pdf) to S3 bucket
2. PutEvent triggers EventBridge which will start state machine execution
3. The Step Function workflow is as below:

![sfn-definition](../architecture/stepfunctions_graph.png)

  - State machine triggers lambda function that extracts data from lease document using Textract
  - Then, state machine triggers two lambda functions in parallel:
    - Contract validation: verify the contract has required fields
    - Compliance check: verify the contract meets the leasing regulation compliance
  - Upon verifying valid contract: 
    - Insert lease data in DynamoDB Lease Table
    - Put them in SQS queue to be processed by different applications
    - Send email notification to user about the contract verified
  - Upon verifying invalid contract:
    - Send email notification to user about invalid contract

For compliance validation, the lambda function checks the ABN against ABN Lookup web services. In order to access it, you will need to gain GUID from Australian Business Register  - https://abr.business.gov.au/Tools/WebServicesAgreement 

The actual contract data extraction and validation logic may be different and much more sophisticated. However, for the sake of simplicity, we are considering payload which has the most basic data that constitutes a lease document and simple validation logic that does the minimal validation check. 

## Deploy the sample application

To build and deploy your application for the first time, run the following in your shell:

```bash
sam build
sam deploy --guided
```

The first command will build the source of your application. The second command will package and deploy your application to AWS, with a series of prompts. You will also need to provide below parameter

* **Email**: The email address that will be used for SNS subscription
* **ABNLookupGUID**: GUID that will be used to access ABN Lookup web services

## Tests

Tests are defined in the `tests` folder in this project. Use PIP to install the test dependencies and run tests.

```bash
lease-verification-service$ pip3 install -r tests/requirements.txt --user
lease-verification-service$ cd tests

# unit test
# Use POWERTOOLS_IDEMPOTENCY_DISABLED=1 to disable the Lambda Powertool Idempotency for unit testing
tests$ POWERTOOLS_IDEMPOTENCY_DISABLED=1 python3 -m pytest unit

# integration test, requiring deploying the stack first.
# Create the env variable AWS_SAM_STACK_NAME with the name of the stack we are testing
tests$ AWS_SAM_STACK_NAME="lease-verification-service" python -m pytest integration -v
```
