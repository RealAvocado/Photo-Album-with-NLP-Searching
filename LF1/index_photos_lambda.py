import json
import boto3
import requests

from datetime import datetime
from requests.auth import HTTPBasicAuth

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    rekognition = boto3.client('rekognition', region_name='us-east-1')

    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        # Step i: Detect labels using Rekognition
        response = rekognition.detect_labels(
            Image={
                'S3Object': {
                    'Bucket': bucket,
                    'Name': key
                }
            }
        )
        labels = [label['Name'] for label in response['Labels']]

        # Step ii: Retrieve metadata
        metadata = s3.head_object(Bucket=bucket, Key=key)
        custom_labels = json.loads(metadata.get('x-amz-meta-customLabels', '[]'))

        # Combine labels from Rekognition and custom labels
        labels.extend(custom_labels)

        # Step iii: Store JSON object in ElasticSearch
        opensearch_payload = {
            'objectKey': key,
            'bucket': bucket,
            'createdTimestamp': datetime.now().isoformat(),
            'labels': labels
        }

        # Assuming you have an ElasticSearch endpoint configured in your Lambda function
        opensearch_endpoint = "https://search-photos-a2wikxciocdgnhqczvcuy6zzqa.us-east-1.es.amazonaws.com"
        insert_into_opensearch(opensearch_payload, opensearch_endpoint)

    return {
        'statusCode': 200,
        'body': json.dumps('Indexing complete!')
    }

def insert_into_opensearch(json_data, opensearch_endpoint):
    username = 'opensearch-user'
    password = 'h7-VUV21[o87hbtyuR'
    headers = {'Content-Type': 'application/json'}

    host = opensearch_endpoint
    index = 'photos'
    datatype = '_doc'
    url = host + '/' + index + '/' + datatype

    response = requests.post(url, auth=HTTPBasicAuth(username, password), headers=headers, json=json_data)

    if response.status_code == 200 or response.status_code == 201:
        print(f"Request successful. Response: {response.text}")
    else:
        print(f"HTTP request failed，Response: {response.status_code}, Body: {response.text}")

    return response
