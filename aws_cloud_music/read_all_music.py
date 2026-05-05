# Used for testing reading from DynamoDB within an EC2 instance Python3

import boto3

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table("music")

all_items = []
response = table.scan()
all_items.extend(response["Items"])

while "LastEvaluatedKey" in response:
    response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
    all_items.extend(response["Items"])

for i, item in enumerate(all_items, start=1):
    print(f"Song {i}")
    print(f"  Title: {item.get('title', '')}")
    print(f"  Artist: {item.get('artist', '')}")
    print(f"  Album: {item.get('album', '')}")
    print(f"  Year: {item.get('year', '')}")
    print(f"  Song ID: {item.get('song_id', '')}")
    print(f"  Album Title: {item.get('album_title', '')}")
    print(f"  Artist Title: {item.get('artist_title', '')}")
    print(f"  S3 Image URL: {item.get('s3_img_url', '')}")
    print("-" * 50)

print(f"Total songs: {len(all_items)}")