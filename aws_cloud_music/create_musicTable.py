import boto3
from botocore.exceptions import ClientError

REGION = "us-east-1"
TABLE_NAME = "music"


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
            {"AttributeName": "artist", "KeyType": "HASH"},
            {"AttributeName": "album_title", "KeyType": "RANGE"}
        ],

        AttributeDefinitions=[
            {"AttributeName": "artist", "AttributeType": "S"},
            {"AttributeName": "album_title", "AttributeType": "S"},
            {"AttributeName": "year", "AttributeType": "S"},
            {"AttributeName": "album", "AttributeType": "S"},
            {"AttributeName": "artist_title", "AttributeType": "S"}
        ],

        LocalSecondaryIndexes=[
            {
                "IndexName": "artist-year-index",
                "KeySchema": [
                    {"AttributeName": "artist", "KeyType": "HASH"},
                    {"AttributeName": "year", "KeyType": "RANGE"}
                ],
                "Projection": {
                    "ProjectionType": "ALL"
                }
            }
        ],

        GlobalSecondaryIndexes=[
            {
                "IndexName": "album-artist-index",
                "KeySchema": [
                    {"AttributeName": "album", "KeyType": "HASH"},
                    {"AttributeName": "artist_title", "KeyType": "RANGE"}
                ],
                "Projection": {
                    "ProjectionType": "ALL"
                }
            }
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