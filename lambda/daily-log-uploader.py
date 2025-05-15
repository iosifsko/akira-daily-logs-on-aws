import boto3
import datetime
import requests
import os

def lambda_handler(event, context):
    # Get today's date
    today = datetime.datetime.utcnow().strftime('%Y-%m-%d')
    filename = f"{today}.txt"
    bucket = os.environ['S3_BUCKET']
    wp_url = os.environ['WP_URL']
    wp_user = os.environ['WP_USER']
    wp_app_password = os.environ['WP_APP_PASSWORD']

    s3 = boto3.client('s3')

    try:
        # Get the log file from S3
        file_obj = s3.get_object(Bucket=bucket, Key=filename)
        content = file_obj['Body'].read().decode('utf-8')

        # Format the post for WordPress
        post = {
            'title': f'Daily Log - {today}',
            'content': content,
            'status': 'publish'
        }

        # Send to WordPress
        response = requests.post(
            f"{wp_url}/wp-json/wp/v2/posts",
            auth=(wp_user, wp_app_password),
            json=post
        )

        if response.status_code == 201:
            return { 'status': 'success', 'message': f'Posted {filename}' }
        else:
            return { 'status': 'error', 'response': response.text }

    except Exception as e:
        return { 'status': 'error', 'message': str(e) }
