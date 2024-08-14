import json
import boto3
import base64
import logging
import os
from decimal import Decimal
import re

max_token = int(os.environ.get("MAX_TOKENS", "4096"))
tmp = float(os.environ.get("TEMPERATURE", "0.25"))
top_p = float(os.environ.get("TOP_P", "0.75"))

bedrock_client = boto3.client("bedrock-runtime")
s3_client = boto3.client("s3")

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def fix_json_errors(json_string):
    # Fix JSON errors using regex
    json_string = re.sub(r'(\})(\s*)(\{)', r'\1,\3', json_string)
    json_string = re.sub(r'(\})(\s*)(\")', r'\1,\3', json_string)
    json_string = re.sub(r'(\d)(\s*\{)', r'\1,\2', json_string)
    json_string = re.sub(r'([{,]\s*)([a-zA-Z_]+[a-zA-Z0-9_]*)\s*:', r'\1"\2":', json_string)
    json_string = re.sub(r'(\w+:)(\s*)([\'\"])?([^\s,]+)([\'\"])?', r'\1 "\4"', json_string)
    json_string = re.sub(r'(?<=:\s)0+(\d+)(?=\s*[,\}])', r'"\1"', json_string)
    return json_string


def safe_json_loads(json_string):
    # Safely load JSON with error handling
    try:
        return json.loads(json_string, parse_float=Decimal)  # Convert floats to Decimal
    except json.JSONDecodeError as e:
        logger.error(f"Initial JSONDecodeError: {e}")
        fixed_json_string = fix_json_errors(json_string)
        try:
            return json.loads(fixed_json_string, parse_float=Decimal)  # Convert floats to Decimal
        except json.JSONDecodeError as e:
            logger.error(f"Fixed JSONDecodeError: {e}")
            raise e


def lambda_handler(event, context):
    try:
        # TODO implement
        body = json.loads(event['Records'][0]['body'])
        logger.info(f"Got the Event: {body}")
        # Extract the bucket name and object key
        bucket_name = body['Records'][0]['s3']['bucket']['name']
        prefix = body['Records'][0]['s3']['object']['key']
        file_name = prefix.split('/')[-1]
        logger.info(f"Got the File: {file_name}")
        response = s3_client.get_object(Bucket=bucket_name, Key=prefix)
        image_bytes = response['Body'].read()

        system_prompt = "You are Document Extractor tool, which will read Images content, and return data into Json format."
        prompt = """
        You are Document Extractor Tool, you will be dealing with Indian Legal Documents. You need to analyse document Images and return a Json data as output.

        Documents could be (Any Indian Legal Document):
        - Aadhar card
        - Passport
        - PAN Card
        - Ration Card
        - MAA Card
        - Driving License
        - Abha Card

        Make sure of following:
        - No other content should be there apart from output json.
        - Document could be in any Indian Language but your output should have data in English only.
        - First two keys of json should be DocumentType, DocumentLanguage, in this you can mention type of document, and language of Document which is found in image.
        - Now in 3rd key of Json should be DocumentExtraction, and here you can put information related to the document.
        - Make sure you are following this structure strictly. 
        """
        # - If there's any PIL information, hide it with XXXX, show the last 3-4 digit only for verification.

        encoded_image = base64.b64encode(image_bytes).decode('utf-8')
        body = json.dumps(
            {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_token,
                "temperature": tmp,
                "top_p": top_p,
                "system": system_prompt,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": encoded_image,
                                },
                            },
                            {"type": "text", "text": prompt},
                        ],
                    }
                ],
            }
        )

        response = bedrock_client.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            body=body,
            accept="application/json",
            contentType="application/json"
        )
        response_body = response.get('body').read().decode('utf-8')
        response_json = json.loads(response_body)
        content_text = response_json['content'][0]['text']
        logger.info(f"Response from Bedrock model: {content_text}")

        result = safe_json_loads(content_text)

        logger.info(f"Extraction: {result}")

        # Create JSON file content
        json_content = json.dumps(result, indent=4)
        json_file_name = file_name.rsplit('.', 1)[0] + '.json'
        json_prefix = f"Indian-Document-Extractor/Output-Data/{json_file_name}"

        # Upload JSON file to S3
        s3_client.put_object(Bucket=bucket_name, Key=json_prefix, Body=json_content, ContentType='application/json')
        logger.info(f"{json_file_name} uploaded successfully to {json_prefix}")

        return {
            'statusCode': 200,
            'body': json.dumps(f"{file_name} processed successfully!")
        }
    except Exception as e:
        logger.error(e)
        return {
            'statusCode': 400,
            'body': json.dumps(str(e))
        }
