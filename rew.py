import json
import logging
import boto3
from botocore.exceptions import ClientError
from urllib.parse import unquote_plus

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")

def lambda_handler(event, context):
    logger.info("S3 event received: %s", json.dumps(event))
    
    secret_name = "prod"
    region_name = "eu-north-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    secret = get_secret_value_response['SecretString']
    print(">>>>",secret)

    # 1. Extract bucket & key
    record = event["Records"][0]
    bucket = record["s3"]["bucket"]["name"]
    key = unquote_plus(record["s3"]["object"]["key"])

    logger.info("Bucket: %s", bucket)
    logger.info("Key: %s", key)

    # 2. Read file from S3
    response = s3.get_object(Bucket=bucket, Key=key)
    file_content = response["Body"].read().decode("utf-8")

    # 3. Parse JSON
    data = json.loads(file_content)

    logger.info("JSON content: %s", json.dumps(data))

    return {
        "statusCode": 200,
        "body": "JSON processed successfully"
    }


