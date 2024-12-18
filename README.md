# AI QA Slack Bot
A serverless AWS Lambda function that powers an intelligent Q&A bot for Slack, leveraging Amazon Bedrock for AI capabilities and multiple data sources for contextual responses.

## Overview
This Slack bot can answer questions by analyzing various data sources including:
- Slack channel history
- Jira tickets
- Confluence wiki pages
- GitHub repositories
- SQL/Athena DDL
- Recruitment data
- General knowledge (via Amazon Bedrock)

## Features
- Multiple operation modes triggered by specific keywords:
  - `slackmode`: Analyzes recent channel history
  - `jiramode`: Searches completed Jira tickets
  - `wikimode`: Searches Confluence wiki content
  - `sqlmode`: Analyzes Athena database schemas
  - `solarmode`: Searches Solution Architect GitHub docs
  - `gitmode`: Searches Git repositories
  - `recruit3r`: Assists with recruitment by analyzing job descriptions and resumes
  - `qa_helper`: Generates interview questions
  - `yodamode`: Direct AI interaction without context

## Prerequisites
- AWS Account with access to:
  - Lambda
  - Bedrock
  - S3
  - IAM
- Slack Workspace with:
  - Bot User OAuth Token
  - Appropriate bot permissions
- Jira account credentials
- Required environment variables:
  - `token`: Slack Bot User OAuth Token
  - `sc`: Jira authentication token

## Setup
1. Create an S3 bucket to store context files:
   - `qry_hist.csv`: Query history
   - `dpd_all.csv`: GitHub documentation
   - `all_docz-2.csv`: Wiki content
   - `primo2.csv`: SQL DDL information
   - `jdesc.txt`: Job descriptions
   - `res_out.txt`: Resume data

2. Configure Slack Event Subscriptions:
   - Subscribe to bot mention events
   - Point to Lambda function URL

3. Set up required IAM roles with permissions for:
   - Lambda execution
   - S3 access
   - Bedrock invocation

## Usage
Mention the bot in Slack with the desired mode and question:
```
@bot slackmode What was discussed about the project yesterday?
@bot wikimode What is our deployment process?
@bot jiramode What tickets were completed this week?
```

## Technical Details
- Runtime: Python
- Main dependencies:
  - `pandas`: Data manipulation
  - `boto3`: AWS SDK
  - `urllib3`: HTTP client
  - `atlassian-python-api`: Jira integration

## Function Flow
1. Receives Slack event
2. Checks for duplicate messages
3. Identifies operation mode
4. Retrieves relevant context data
5. Calls Amazon Bedrock for AI processing
6. Posts response back to Slack channel

## Maintenance
- Monitor S3 storage for context files
- Update environment variables as needed
- Review and update AI prompt templates
- Maintain Jira/Slack credentials

## Error Handling
- Duplicate message detection
- Context retrieval fallbacks
- API error handling for Slack/Jira
- Response size limitations

## Security Considerations
- Secure storage of credentials
- Limited S3 bucket access
- Slack authentication
- API token management

## Contributing
1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request
