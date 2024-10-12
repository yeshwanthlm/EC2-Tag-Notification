# EC2 Tag Notification
Automated notifications when EC2 Instances are missing a specific tag

![WhatsApp Image 2024-10-12 at 10 20 26](https://github.com/user-attachments/assets/6415405e-83b8-40c8-a5c2-b29cda6faa0a)

To achieve automated notifications when EC2 instances are missing a specific tag (like the Environment tag), you can leverage a combination of AWS services such as AWS Lambda, AWS CloudWatch, and Amazon SNS. Here's a step-by-step guide for implementing this solution:

## Solution Overview
1. CloudWatch Events (EventBridge): Will trigger periodically to check for EC2 instances.
2. Lambda Function: Will be invoked by the event to check for instances that do not have the required tag or its value is missing.
3. SNS Topic: Sends an email notification when such instances are found.

## Steps
1. Create an SNS Topic for Email Notifications
  * Go to the Amazon SNS Console and create a topic (e.g., MissingTagNotifications).
  * Choose the topic type as Standard.
  * Give it a name and create the topic.
  * Create a subscription to this SNS topic with your email address, and confirm the subscription via the email you receive.

2. Create a Lambda Function to Check EC2 Instances
  * Go to the AWS Lambda Console and create a new Lambda function.
  * Choose "Author from scratch," give it a name (e.g., CheckEC2Tags), and use a Python runtime.
  * Attach the necessary permissions to the Lambda function:
  * EC2 DescribeInstances permission to read instance tags.
  * SNS Publish permission to send notifications.

Here's a sample Python code for the Lambda function:
```
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

```


3. Configure Lambda Environment Variables
  * After creating the Lambda function, set the following environment variable:
  * SNS_TOPIC_ARN: Set this to the ARN of the SNS topic created earlier.

4. Create a CloudWatch Rule (EventBridge)
  * Go to the CloudWatch Console and create a rule.
  * Select Event Source as EventBridge and choose a schedule (e.g., every five minutes).
  * To run the EventBridge rule every 5 minutes, you can use the following cron expression:
    ```
    cron(0/5 * * * ? *)
    ```
  * Set the target as the Lambda function you created (CheckEC2Tags).

5. Test the Solution
You can either manually run the Lambda function from the console to verify that it is checking for instances without the tag or wait for the CloudWatch rule to trigger the Lambda function based on your schedule.
If any instances are missing the required Environment tag or its value, you will receive an email notification listing the instance IDs.
