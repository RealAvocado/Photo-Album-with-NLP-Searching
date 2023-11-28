import json
import boto3
from datetime import datetime

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    rekognition = boto3.client('rekognition')
    es = boto3.client('es')

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
        custom_labels = json.loads(metadata.get('Metadata', {}).get('x-amz-meta-customLabels', '[]'))

        # Combine labels from Rekognition and custom labels
        labels.extend(custom_labels)

        # Step iii: Store JSON object in ElasticSearch
        es_payload = {
            'objectKey': key,
            'bucket': bucket,
            'createdTimestamp': metadata['LastModified'].isoformat(),
            'labels': labels
        }

        # Assuming you have an ElasticSearch endpoint configured in your Lambda function
        es.index(index='photos', doc_type='_doc', body=json.dumps(es_payload))

    return {
        'statusCode': 200,
        'body': json.dumps('Indexing complete!')
    }
