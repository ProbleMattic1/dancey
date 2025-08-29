import os, boto3

def s3_client():
    endpoint = os.getenv("S3_ENDPOINT")
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    region = os.getenv("AWS_REGION","us-east-1")
    return boto3.client("s3",
        endpoint_url=endpoint,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region,
        config=boto3.session.Config(signature_version='s3v4'))

def parse_s3_uri(uri: str):
    assert uri.startswith("s3://")
    rest = uri[len("s3://"):]
    bucket, key = rest.split("/", 1)
    return bucket, key
