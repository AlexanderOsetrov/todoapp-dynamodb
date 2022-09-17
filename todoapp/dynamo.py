import os
import boto3


DB_URL = os.environ.get('DYNAMODB_URL', 'http://dynamodb:8000')
dynamodb_resource = boto3.resource('dynamodb', endpoint_url=DB_URL)
dynamodb_client = boto3.client('dynamodb', endpoint_url=DB_URL)


def create_or_get_table():
    tables = dynamodb_client.list_tables()['TableNames']
    if 'items' not in tables:
        table = dynamodb_resource.create_table(
            TableName='items',
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        )
        return table
    else:
        return dynamodb_resource.Table('items')
