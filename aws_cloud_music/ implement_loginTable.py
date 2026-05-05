import time
import boto3
from botocore.exceptions import ClientError

REGION = "us-east-1"
TABLE_NAME = "login"

LOGIN_ITEMS = [
    {
        "email": "s40608655@student.rmit.edu.au",
        "password": "567890",
        "user_name": "HantaoShen5"
    },
    {
        "email": "s40608658@student.rmit.edu.au",
        "password": "890123",
        "user_name": "HantaoShen8"
    },
    {
        "email": "s40608650@student.rmit.edu.au",
        "password": "012345",
        "user_name": "HantaoShen0"
    },
    {
        "email": "s40608656@student.rmit.edu.au",
        "password": "678901",
        "user_name": "HantaoShen6"
    },
    {
        "email": "s40608657@student.rmit.edu.au",
        "password": "789012",
        "user_name": "HantaoShen7"
    },
    {
        "email": "s40608659@student.rmit.edu.au",
        "password": "901234",
        "user_name": "HantaoShen9"
    },
    {
        "email": "s40608652@student.rmit.edu.au",
        "password": "234567",
        "user_name": "HantaoShen2"
    },
    {
        "email": "s40608653@student.rmit.edu.au",
        "password": "345678",
        "user_name": "HantaoShen3"
    },
    {
        "email": "s40608651@student.rmit.edu.au",
        "password": "123456",
        "user_name": "HantaoShen1"
    },
    {
        "email": "s40608654@student.rmit.edu.au",
        "password": "456789",
        "user_name": "HantaoShen4"
    }
]


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
            {
                "AttributeName": "email",
                "KeyType": "HASH"
            }
        ],
        AttributeDefinitions=[
            {
                "AttributeName": "email",
                "AttributeType": "S"
            }
        ],
        BillingMode="PAY_PER_REQUEST"
    )
    table.wait_until_exists()
    print(f"Table '{TABLE_NAME}' created successfully.")
    return table


def load_items(table):
    print("Loading login data...")
    with table.batch_writer() as batch:
        for item in LOGIN_ITEMS:
            batch.put_item(Item=item)
    print("All login items inserted successfully.")


def scan_table(table):
    response = table.scan()
    items = response.get("Items", [])

    print(f"\nInserted items count: {len(items)}")
    for item in sorted(items, key=lambda x: x["email"]):
        print(item)


def main():
    dynamodb = get_dynamodb()

    delete_table_if_exists(dynamodb)
    table = create_table(dynamodb)

    # Optional small delay after creation
    time.sleep(2)

    load_items(table)
    scan_table(table)


if __name__ == "__main__":
    main()