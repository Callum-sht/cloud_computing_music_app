# Script to read all users from 'login' table for testing purposes

import boto3

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table("login")

all_items = []
response = table.scan()
all_items.extend(response["Items"])

while "LastEvaluatedKey" in response:
    response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
    all_items.extend(response["Items"])

for i, item in enumerate(all_items, start=1):
    print(f"User {i}")
    print(f"  Email: {item.get('email', '')}")
    print(f"  Password: {item.get('password', '')}")
    print(f"  Username: {item.get('user_name', '')}")
    print("-" * 50)

print(f"Total Users: {len(all_items)}")