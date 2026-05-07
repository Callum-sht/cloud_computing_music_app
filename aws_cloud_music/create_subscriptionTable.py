import boto3
from botocore.exceptions import ClientError

REGION = "us-east-1"
TABLE_NAME = "subscription"


def get_dynamodb():
    return boto3.resource("dynamodb", region_name=REGION)


def delete_table_if_exists(dynamodb):
    try:
        table = dynamodb.Table(TABLE_NAME)
        table.load()
        print(f"Table '{TABLE_NAME}' already exists. Deleting it first...")
        table.delete()
        table.wait_until_not_exists()
        print(f"Table '{TABLE_NAME}' deleted.")
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "ResourceNotFoundException":
            print(f"Table '{TABLE_NAME}' does not exist. No need to delete.")
        else:
            raise


def create_table(dynamodb):
    print(f"Creating table '{TABLE_NAME}'...")

    table = dynamodb.create_table(
        TableName=TABLE_NAME,

        KeySchema=[
            {"AttributeName": "user_email", "KeyType": "HASH"},
            {"AttributeName": "song_id", "KeyType": "RANGE"}
        ],

        AttributeDefinitions=[
            {"AttributeName": "user_email", "AttributeType": "S"},
            {"AttributeName": "song_id", "AttributeType": "S"}
        ],

        BillingMode="PAY_PER_REQUEST"
    )

    table.wait_until_exists()
    print(f"Table '{TABLE_NAME}' created successfully.")
    return table


def main():
    dynamodb = get_dynamodb()
    delete_table_if_exists(dynamodb)
    create_table(dynamodb)


if __name__ == "__main__":
    main()
