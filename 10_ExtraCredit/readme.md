# Extra credit

There are many options to expand on what you've built in the previous modules. 

The challenges here are, pick your battle :)

## Challenge 1: integrate the bot with other messaging platforms

Why not add more channels your customer can use to reach your customer service? Here are some ideas:

* **Facebook Messenger**
	
	See guide [here](http://docs.aws.amazon.com/lex/latest/dg/fb-bot-association.html) on integrating your Lex bot with Facebook Messenger. 

* **Slack**
	
	See guide [here](https://docs.aws.amazon.com/lex/latest/dg/slack-bot-association.html) on integrating your Lex bot with Slack
	
* **Amazon Alexa Skill**

 	See guide [here](https://docs.aws.amazon.com/lex/latest/dg/export-to-alexa.html) on exporting your Lex bot to an Alexa skill. 
 	
* **Kik Messenger** 
 
 	See guide [here](http://docs.aws.amazon.com/lex/latest/dg/kik-bot-association.html) on integrating your Lex bot with Kik Messenger. 

* **Mobile app**
	
	Use [AWS Mobile Hub](http://docs.aws.amazon.com/aws-mobile/latest/developerguide/conversational-bots.html) to generate an Android/iOS mobile app that integrates with your Lex chatbot. 

* **Web app**
 
	Refer to these examples to embed a chatbot in your website powered by Amazon Lex:
	
	* [https://github.com/awslabs/aws-lex-web-ui](https://github.com/awslabs/aws-lex-web-ui)
	* [“Greetings, visitor!” — Engage Your Web Users with Amazon Lex](https://aws.amazon.com/blogs/ai/greetings-visitor-engage-your-web-users-with-amazon-lex/)
	* [Capturing Voice Input in a Browser and Sending it to Amazon Lex
](https://aws.amazon.com/blogs/ai/capturing-voice-input-in-a-browser/)

* **Any Messenging service**
	Refer to this blog post to integrate your Lex bot with any messenging service:
	
	* [https://aws.amazon.com/blogs/ai/integrate-your-amazon-lex-bot-with-any-messaging-service/](https://aws.amazon.com/blogs/ai/integrate-your-amazon-lex-bot-with-any-messaging-service/)
	
## Challenge 2: make the bot support additional intents

The business logic behind the well site visit bot has been written to support additional intents beyond just checking the fluid level and recording a site visit.

* Add a `GetProductionStats` intent with these properties:
	* Utterances:
		* `production at {wellsiteId}`
		* `production`
		* `What is the current production`
		* `What is the current production at {wellsiteId}`
	* Initialization and validation: `chatbot-workshop-LexBotHandler`
	* 1 slot:
		* Name: `wellsiteId`
		* Slot Type: `WellSiteIdType`
		* Prompt: `What is the well site id?`
		* Required: Yes
	* Fulfillment: AWS Lambda function `chatbot-workshop-LexBotHandler`
* Add a `GetRodReplacement` intent with these properties:
	* Utterances:
		* `rod at {wellsiteId}`
		* `rod`
		* `when was the rod last replaced at {wellsiteId}`
	* Initialization and validation: `chatbot-workshop-LexBotHandler`
	* 1 slot:
		* Name: `wellsiteId`
		* Slot Type: `WellSiteIdType`
		* Prompt: `What is the well site id?`
		* Required: Yes
	* Fulfillment: AWS Lambda function `chatbot-workshop-LexBotHandler`

## Challenge 3: build a bot for your own customer service use case

What do your customers need help with? 
