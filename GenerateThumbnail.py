import boto3
import os
from PIL import Image
from io import BytesIO

# Please Note, Lambda Layers Need to Be Created for External Libraries

class ProcessThumbnail:

    def __init__(self):
        self.s3_client = boto3.client('s3')
        self.bucket_name = os.environ['BUCKET_NAME']
        self.thumbnail_folder = 'Thumbnails/'


    def generate_thumbnail(self, image_key):
        try:
            image_name = image_key.split('/')[-1]
            thumbnail_key = 'Thumbnail/' + image_name

            crop_lengths = (300, 300, 300, 300)

            s3_response = self.s3_client.get_object(Bucket=self.bucket_name, Key=image_key)
            image_data = s3_response['Body'].read()

            # Here, we also have option of using 10 GB ephermal storage of AWS Lambda istead of using Streams
            image = Image.open(BytesIO(image_data))

            cropped_image = image.crop(crop_lengths)

            with BytesIO() as output:
                cropped_image.save(output, format='JPEG')
                output.seek(0)
                self.s3_client.put_object(Bucket=self.bucket_name, Key=thumbnail_key, Body=output)

            return True
        
        except Exception as e:
            print(f"Error receiving messages: {str(e)}")
            return False
       

class SQSReader:
   def __init__(self):
        self.sqs_client = boto3.client('sqs')
        self.queue_url =  os.environ['SQS_QUEUE_URL']

   def read_messages(self, max_messages=4, visibility_timeout=30, wait_time_seconds=10):
        try:
            response = self.sqs_client.receive_message( 
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=max_messages,
                VisibilityTimeout=visibility_timeout,
                WaitTimeSeconds=wait_time_seconds
            )

            if 'Messages' in response:
                return [(message['Body']['object_key'], message['ReceiptHandle']) for message in response['Messages']]
            
            return []

        except Exception as e:
            print(f"Error receiving messages: {str(e)}")

   def delete_message(self, receipt_handle):
        try:
            self.sqs_client.delete_message(
                QueueUrl=self.sqs_queue_url,
                ReceiptHandle=receipt_handle
            )
        except Exception as e:
            print(f"Error deleting message: {str(e)}") 

def lambda_handler(event, context):
    print('Input Event: ', event, sep="\n")

    try:
        sqs_reader = SQSReader()
        messages = sqs_reader.read_messages()

        process_thumbnail = ProcessThumbnail()

        for message in messages:
            s3_object_key = message[0]
            receipt_handle = message[1]

            if(process_thumbnail.generate_thumbnail(s3_object_key)):
                # Deleting message from SQS Queue
                sqs_reader.delete_message(receipt_handle)

                print(f"Successfully generated thumbnail for {s3_object_key}")
            else:
                print(f"Failed to generate thumbnail for {s3_object_key}")

    except Exception as e:
        print(f"Error receiving messages: {str(e)}")




   

