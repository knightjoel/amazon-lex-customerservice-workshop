# Build a field service chatbot with Amazon Lex

Amazon Lex allows you to quickly and easily build sophisticated, natural language, chatbots.

In this workshop, you will build a field service chatbot for Octank Energy Services, a fictitious
energy company. They want to make it really easy for their field operators to
get and update information about well sites that they visit.

The application architecture uses [Amazon Lex](https://aws.amazon.com/lex/), [AWS Lambda](https://aws.amazon.com/lambda/) and [Amazon DynamoDB](https://aws.amazon.com/dynamodb/). You will build an Amazon Lex chatbot that understands operators' speech or text inputs. Data about well sites is persisted in DynamoDB. AWS Lambda functions get triggered by Amazon Lex to execute business logic and interact with the database layer. You can then connect the Lex chatbot with twilio SMS, which allows users to access your bot over SMS text messages; or Amazon Connect, which allows users to call a phone number and interact with the bot through voice.

See the diagram below for a depiction of the complete architecture.


<img src="99_resources/architecture_diagram.png" width="100%">

## Prerequisites

### AWS Account

In order to complete this workshop you'll need an AWS Account with sufficient permission to create AWS IAM, Amazon Lex, Amazon Connect, Lambda, DynamoDB and CloudFormation resources. The code and instructions in this workshop assume only one student is using a given AWS account at a time. If you try sharing an account with another student, you'll run into naming conflicts for certain resources. You can work around these by appending a unique suffix to the resources that fail to create due to conflicts, but the instructions do not provide details on the changes required to make this work.

## Modules

This workshop is broken up into multiple modules. For building out your Lex chatbot, you must complete the following module in order before proceeding to the next:

1. [Build a Lex chatbot and handle informational queries](01_LexBotInformational)
1. [Integrate Lex chatbot with Amazon Connect (voice over the phone)](03_AmazonConnectIntegration)
1. [Create the "site visit" intent](05_SiteVisit)

Resource cleanup:

* [Resource clean-up](11_Cleanup)

