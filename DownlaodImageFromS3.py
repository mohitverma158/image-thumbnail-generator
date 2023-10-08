import boto3
import base64
import os

# Global Intialization of AWS Clients & AWS Resources
s3 = boto3.client('s3')

bucket_name = os.environ['BUCKET_NAME']

class ImageDownloader:
    def __init__(self, event):
        self.event = event
    
    def download_file(self):
        try:
            # Fetching the file name from the API Gateway query parameters
            # This needs to be configured while setting up API Gateway
            file_name = self.event['queryStringParameters']['file_name']
            s3_file_name  ='Images/' + file_name

            # Getting the file from S3
            response = s3.get_object(Bucket=bucket_name, Key=s3_file_name)
            file_data = response['Body'].read()

            print('S3 Response:', response, sep="\n")
            
            encoded_file_data = base64.b64encode(file_data).decode('utf-8')

            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': response['ContentType'],  
                    'Content-Disposition': f'attachment; filename="{file_name}"',  # Downlaods with original file name

                },
                'body': encoded_file_data,
                'isBase64Encoded': True
            }
            
        except Exception as e:
            return {
                'statusCode': 500,
                'body': f'Error downloading file: {str(e)}'
            }
        
    def passjd():
        pass

def lambda_handler(event, context):
    print("Input Event: ", event, sep="\n")
    downloader = ImageDownloader(event)
    return downloader.download_file()
    