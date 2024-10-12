import boto3
import os

ec2 = boto3.client('ec2')
sns = boto3.client('sns')

def lambda_handler(event, context):
    # Replace with your SNS topic ARN
    sns_topic_arn = os.environ['SNS_TOPIC_ARN']
    
    # Describe EC2 instances
    instances = ec2.describe_instances()
    
    missing_tag_instances = []
    
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            # Get tags
            tags = instance.get('Tags', [])
            # Check if the 'Environment' tag is missing or empty
            if not any(tag['Key'] == 'Environment' and tag['Value'] for tag in tags):
                missing_tag_instances.append(instance['InstanceId'])
    
    # If any instances are missing the 'Environment' tag, send an SNS notification
    if missing_tag_instances:
        message = f"These EC2 instances are missing the 'Environment' tag: {missing_tag_instances}"
        sns.publish(
            TopicArn=sns_topic_arn,
            Subject="EC2 Instances Missing 'Environment' Tag",
            Message=message
        )
    
    return {
        'statusCode': 200,
        'body': 'Notification sent for missing tag instances.'
    }
