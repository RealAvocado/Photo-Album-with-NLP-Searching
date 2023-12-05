import json
import boto3
import requests

from datetime import datetime
from requests.auth import HTTPBasicAuth


def lambda_handler(event, context):
    s3 = boto3.client('s3', region_name='us-east-1')
    rekognition = boto3.client('rekognition', region_name='us-east-1')

    opensearch_endpoint = "https://search-photos-a2wikxciocdgnhqczvcuy6zzqa.us-east-1.es.amazonaws.com"
    username = 'opensearch-user'
    password = 'h7-VUV21[o87hbtyuR'

    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        # if a photo with same name (file extension must also be the same in this case)
        # already exists in opensearch index, delete the old one.
        delete_old_photo_with_same_name(opensearch_endpoint, username, password, 'photos', key)

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
        sys.stdout.write(str(metadata))
        custom_labels = metadata['Metadata'].get('customlabels', None)

        # Combine labels from Rekognition and custom labels
        if custom_labels is not None:
            labels.append(custom_labels.split(','))

        # Step iii: Store JSON object in OpenSearch
        opensearch_payload = {
            'objectKey': key,
            'bucket': bucket,
            'createdTimestamp': datetime.now().isoformat(),
            'labels': labels
        }
        insert_into_opensearch(opensearch_payload, opensearch_endpoint, HTTPBasicAuth(username, password))

    return {
        'statusCode': 200,
        'body': json.dumps('Indexing complete!')
    }


def insert_into_opensearch(json_data, opensearch_endpoint, http_auth):
    headers = {'Content-Type': 'application/json'}
    host = opensearch_endpoint
    index = 'photos'
    datatype = '_doc'
    url = host + '/' + index + '/' + datatype

    response = requests.post(url, auth=http_auth, headers=headers, json=json_data)

    if response.status_code == 200 or response.status_code == 201:
        print(f"Request successful. Response: {response.text}")
    else:
        print(f"HTTP request failed，Response: {response.status_code}, Body: {response.text}")

    return response


def delete_old_photo_with_same_name(opensearch_endpoint, username, password, index, photo_name):
    search_url = opensearch_endpoint + '/' + index + '/' + '_search?q=' + photo_name
    response = requests.get(search_url, auth=HTTPBasicAuth(username, password))
    response = json.loads(response.content.decode('utf-8'))
    hit_number = response['hits']['total']['value']

    if hit_number > 0:
        document_id = response['hits']['hits'][0]['_id']
        delete_url = opensearch_endpoint + '/' + index + '/' + '_doc' + '/' + document_id
        delete_response = requests.delete(delete_url, auth=HTTPBasicAuth(username, password))


{
    'ResponseMetadata':
     {
        'RequestId': 'AQCCDS58SV29GRP9',
        'HostId': 'Ao23PzICP0iu01BvK+K3Lro0F86P95DGCp8iz5yLqVSJdbyTvt0d9Vw6Ia2PUsr1hjSxyN7La+4=',
        'HTTPStatusCode': 200, 'HTTPHeaders': {
        'x-amz-id-2': 'Ao23PzICP0iu01BvK+K3Lro0F86P95DGCp8iz5yLqVSJdbyTvt0d9Vw6Ia2PUsr1hjSxyN7La+4=',
        'x-amz-request-id': 'AQCCDS58SV29GRP9', 'date': 'Tue, 05 Dec 2023 19:36:17 GMT',
        'last-modified': 'Tue, 05 Dec 2023 19:36:09 GMT', 'etag': '"368ea2e110e2776ece6a019c63dd28d0"',
        'x-amz-server-side-encryption': 'AES256', 'x-amz-meta-customlabels': 'cute&fat', 'accept-ranges': 'bytes',
        'content-type': 'image/jpeg', 'server': 'AmazonS3', 'content-length': '51937'
     },
      'RetryAttempts': 0
      },
    'AcceptRanges': 'bytes',
    'LastModified': datetime.datetime(2023, 12, 5, 19, 36, 9, tzinfo=tzutc()),
    'ContentLength': 51937,
    'ETag': '"368ea2e110e2776ece6a019c63dd28d0"',
    'ContentType': 'image/jpeg',
    'ServerSideEncryption': 'AES256',
    'Metadata':
        {
            'customlabels': 'cute&fat'
        }
 }