import os
import boto3
import json
import base64

# Global Intialization of AWS Clients & AWS Resources
s3 = boto3.client('s3')

bucket_name = os.environ['BUCKET_NAME']

class ImageUploader:
    def __init__(self, event):
        self.event = event
    
    def upload_image(self):
        try:
            file_data = self.event['body']
            file_name = self.event['queryStringParameters']['file_name']
            s3_file_name  ='Images/' + file_name
            
            s3.put_object(Bucket=bucket_name, Key=s3_file_name, Body=file_data)

            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'File uploaded successfully'})
            }

        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': str(e)})
            }

def lambda_handler(event, context):
    print('Input Event: ', event, sep="\n")
    uploader = ImageUploader(event)
    return uploader.upload_image()
