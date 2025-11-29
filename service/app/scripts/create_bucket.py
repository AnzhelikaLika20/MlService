import boto3
from botocore.exceptions import ClientError
from app.config import settings

def create_bucket(bucket_name: str):
    s3 = boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT,
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        region_name=settings.S3_REGION,
    )
    try:
        existing_buckets = [b["Name"] for b in s3.list_buckets()["Buckets"]]
        if bucket_name in existing_buckets:
            print(f"Bucket '{bucket_name}' уже существует")
            return

        s3.create_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' успешно создан")
    except ClientError as e:
        print(f"Ошибка при создании бакета: {e}")

if __name__ == "__main__":
    create_bucket(settings.S3_BUCKET)
