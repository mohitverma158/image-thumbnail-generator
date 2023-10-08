import boto3
import json
import os

# Global Intialization of AWS Clients & AWS Resources
sqs_client = boto3.client('sqs')

sqs_queue_url = os.environ['SQS_QUEUE_URL']

def lambda_handler(event, context):
    try:
        print("Input Event: ", event, sep="\n")

        s3_event = event['Records'][0]['s3']
        object_key = s3_event['object']['key']

        message_body = {
            'bucket': s3_event['bucket']['name'],
            'object_key': object_key,
            'event_name': event['Records'][0]['eventName']
        }

        print("Message Body: ", message_body, sep="\n")

        # Publishingthe message to SQS
        response = sqs_client.send_message(
            QueueUrl=sqs_queue_url,
            MessageBody=json.dumps(message_body)
        )

        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            status_code = 200
            status_message = 'Successfully published message to SQS'    
        else:
            status_code = 500
            status_message = 'Failed to publish message to SQS'
        
        print("SQS Response: ", response, "Status Code: ", status_code, "Status Message: ", status_message, sep="\n")

        return {
                'statusCode': status_code,
                'body': status_message
            }
    
    except Exception as e:
        status_code = 500
        status_message = f'Error: {str(e)}'

        print("EXCEPTION OCCURED!" , "Status Code: ", status_code, "Status Message: ", status_message, sep="\n")

        return {
            'statusCode': 500,
            'body': status_message
        }