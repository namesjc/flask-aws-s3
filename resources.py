import boto3
from flask import session
from config import S3_BUCKET, S3_KEY, S3_SECRET


def _get_s3_resource():
    s3_session = boto3.session.Session()
    if S3_KEY and S3_SECRET:
        return s3_session.resource(
            service_name="s3",
            verify=False,
            aws_access_key_id=S3_KEY,
            aws_secret_access_key=S3_SECRET,
        )
    else:
        return boto3.resource("s3")


def _get_s3_client():
    s3_session = boto3.session.Session()
    if S3_KEY and S3_SECRET:
        return s3_session.client(
            service_name="s3",
            verify=False,
            aws_access_key_id=S3_KEY,
            aws_secret_access_key=S3_SECRET,
        )
    else:
        return boto3.resource("s3")


def get_bucket():
    s3_resource = _get_s3_resource()
    if "bucket" in session:
        bucket = session["bucket"]
    else:
        bucket = S3_BUCKET
    return s3_resource.Bucket(bucket)


def get_buckets_list():
    s3_client = _get_s3_client()
    return s3_client.list_buckets().get("Buckets")


def generate_presigned_url(my_bucket, filename):
    s3_client = _get_s3_client()
    url = s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": my_bucket, "Key": filename},
        ExpiresIn=3000,
    )
    return url


def get_bucket_folder(bucket_name):
    s3_client = _get_s3_client()
    resp = s3_client.list_objects_v2(Bucket=bucket_name, Prefix="", Delimiter="/")
    if "CommonPrefixes" in resp:
        folders = [x["Prefix"] for x in resp["CommonPrefixes"]]
        return folders
