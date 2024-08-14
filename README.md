# Indian🇮🇳 Legal Document Extractor using AWS Bedrock, Lambda, and SQS

### [Watch this tutorial►](https://youtu.be/YWmnD_QcZQU)
<img src="https://github.com/Spidy20/AWS-Assistant-RAG-ChatBot/blob/master/yt_thumbnail.jpg">

- In this tutorial, we'll be creating a GPT-4 AWS Helper ChatBot utilizing Langchain, Lambda, API Gateway, and PostgreSQL PGVector hosted on an EC2 instance as our Vector database.

### Implementation Architecture
<img src="https://github.com/Spidy20/AWS-Assistant-RAG-ChatBot/blob/master/AWS-Assistant-ChatBot-Architecture.png">

### Used Services
- **AWS Lambda**: Responsible for managing the backend of the Document Extractor using the Boto3 SDK.
- **AWS SQS**: Manages the scalability of solutions by maintaining a queue, enabling multiple documents to be processed.
- **Bedrock Claude Sonnet Model**: Used to extract JSON data from legal documents.
- **S3**: Stores images of legal documents and triggers SQS with a Lambda function upon upload.

### Implementation Setup
- Creating an S3 Bucket.
- Creating a Lambda function and lambda handler.
- Setting up the SQS Queue and Policy.
- Configuring S3 event to trigger SQS with AWS Lambda
- Testing the automation workflow.
- Testing with Indian legal documents.



### Give Star⭐ to this repository, and fork it to support me. 

### [Buy me a Coffee☕](https://www.buymeacoffee.com/spidy20)
### [Donate me on PayPal(It will inspire me to do more projects)](https://www.paypal.me/spidy1820)
