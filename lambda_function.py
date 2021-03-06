"""
This sample demonstrates an implementation of the Lex Code Hook Interface
in order to serve a sample bot which manages reservations for hotel rooms and car rentals.
Bot, Intent, and Slot models which are compatible with this sample can be found in the Lex Console
as part of the 'BookTrip' template.

For instructions on how to set up and test this bot, as well as additional samples,
visit the Lex Getting Started documentation http://docs.aws.amazon.com/lex/latest/dg/getting-started.html.
"""

import json
import datetime
import time
import os
import dateutil.parser
import logging
import re
import boto3
from boto3.dynamodb.conditions import Key, Attr

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


# --- Helpers that build all of the responses ---


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }


def confirm_intent(session_attributes, intent_name, slots, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ConfirmIntent',
            'intentName': intent_name,
            'slots': slots,
            'message': message
        }
    }


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }


# --- Helper Functions ---
def retrieve_from_session(session, key):
    value = None
    if key in session:
        logger.debug('looking for record={} in session'.format(key))
        value = json.loads(session[key])
    return value

def retrieve_operator_record(operatorName):
    dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
    tablename = os.environ['OPERATOR_DDB_TABLE']
    logger.debug('table={}'.format(tablename))
    table = dynamodb.Table(tablename)
    response = table.get_item(
        Key={
            'operatorName': operatorName
        }
    )
    if 'Item' in response:
        return response['Item']
    else:
        return None

def retrieve_wellsite_location_record(wellsiteId):
    dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
    tablename = os.environ['WELL_SITE_LOCATION_DDB_TABLE']
    logger.debug('table={}'.format(tablename))
    table = dynamodb.Table(tablename)
    response = table.get_item(
        Key={
            'wellSiteId': wellsiteId
        }
    )
    if 'Item' in response:
        return response['Item']
    else:
        return None

def retrieve_wellsite_visit_record(wellsiteId):
    dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
    tablename = os.environ['WELL_SITE_VISIT_DDB_TABLE']
    logger.debug('table={}'.format(tablename))
    table = dynamodb.Table(tablename)
    response = table.query(
        KeyConditionExpression=Key('wellSiteId').eq(wellsiteId)
    )
    #response = table.get_item(
    #    Key={
    #        'wellSiteId': wellsiteId
    #    }
    #)
    if response['Count'] == 0:
        return None
    else:
        return response['Items'][0]

def addWellsiteVisitRecordToDynamo(wellsite_visit_record):
    dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
    tablename = os.environ['WELL_SITE_VISIT_DDB_TABLE']
    logger.debug('table={}'.format(tablename))
    table = dynamodb.Table(tablename)
    logger.debug('item={}'.format(wellsite_visit_record))
    table.put_item(Item=wellsite_visit_record)


def safe_int(n):
    """
    Safely convert n value to int.
    """
    if n is not None:
        return int(n)
    return n



def try_ex(func):
    """
    Call passed in function in try block. If KeyError is encountered return None.
    This function is intended to be used to safely access dictionary.

    Note that this function would have negative impact on performance.
    """

    try:
        return func()
    except KeyError:
        return None



def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False


def get_day_difference(later_date, earlier_date):
    later_datetime = dateutil.parser.parse(later_date).date()
    earlier_datetime = dateutil.parser.parse(earlier_date).date()
    return abs(later_datetime - earlier_datetime).days


def add_days(date, number_of_days):
    new_date = dateutil.parser.parse(date).date()
    new_date += datetime.timedelta(days=number_of_days)
    return new_date.strftime('%Y-%m-%d')


def build_validation_result(isvalid, violated_slot, message_content):
    return {
        'isValid': isvalid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }


def validate_wellsiteid(wellsiteId):

    if not wellsiteId:
        logger.debug("error. wellsite id is not specified")
        return build_validation_result(
            False,
            'wellsiteId',
            'You need to specify a wellsite id of the format 01-01-001-01w5'
        )
    
    pattern = re.compile("^(\d{2}-\d{2}-\d{3}-\d{2}[a-zA-Z][0-9])")
    match = pattern.match(wellsiteId)
    
    if not match:
        logger.debug("error. wellsite id={} does not match expected format".format(wellsiteId))
        return build_validation_result(
            False,
            'wellsiteId',
            'You need to specify a wellsite id of the format 01-01-001-01w5'
        )

    return {'isValid': True}




def production_stats(intent_request):
    """
    Performs dialog management for retrieving wellsite production stats.

    Beyond data retrieval, the implementation for this intent demonstrates the following:
    1) Use of elicitSlot in slot validation and re-prompting
    2) Use of sessionAttributes to pass information that can be used to guide conversation
    """
    logger.debug('intent={}'.format(intent_request['currentIntent']))
    logger.debug('start session={}'.format(intent_request['sessionAttributes']))
    slots = intent_request['currentIntent']['slots']
    wellsite_id = ''
    
    if 'wellsiteId' in slots:
        wellsite_id = slots['wellsiteId']

    confirmation_status = intent_request['currentIntent']['confirmationStatus']
    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
    if not wellsite_id:
        logger.debug('wellsiteid is not specified.  retrieving from session')
        if 'wellsiteId' in session_attributes:
            wellsite_id = try_ex(lambda: session_attributes['wellsiteId'])


    # Validate our slot values.  If any are invalid, re-elicit for their value
    validation_result = validate_wellsiteid(wellsite_id)
    if validation_result['isValid']:
        session_attributes['wellsiteId'] = wellsite_id
    else:
        slots[validation_result['violatedSlot']] = None
        return elicit_slot(
            session_attributes,
            intent_request['currentIntent']['name'],
            slots,
            validation_result['violatedSlot'],
            validation_result['message']
        )


    # load the wellsite visit record
    wellsite_location_record = retrieve_from_session(session_attributes, 'wellsiteLocationRecord')
    
    if not wellsite_location_record or not wellsite_location_record['wellSiteId'] == wellsite_id:
        logger.debug('could not find wellsite record in session or mismatch on wellsite id')
        wellsite_location_record = retrieve_wellsite_location_record(wellsite_id)

    
        if wellsite_location_record is None:
            return elicit_slot(
                session_attributes,
                intent_request['currentIntent']['name'],
                slots,
                'wellsiteId',
                {'contentType': 'PlainText', 'content': 'Could not retrieve details of wellsite {}.  Please try again.'.format(wellsite_id)}
            )
        session_attributes['wellsiteLocationRecord'] = json.dumps(wellsite_location_record)


    # create the response message
    msg = 'Current production is {} barrels of oil and {} barrels of water'.format(wellsite_location_record['oilProductionRate'], wellsite_location_record['waterProductionRate'])
    logger.debug('production_stats msg={}'.format(msg))
    logger.debug('session={}'.format(session_attributes))
    
    return close(
        session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': msg
        }
    )


def session_details(intent_request):
    """
    Performs dialog management for retrieving information stored in session.

    Beyond data retrieval, the implementation for this intent demonstrates the following:
    1) Use of elicitSlot in slot validation and re-prompting
    2) Use of sessionAttributes to pass information that can be used to guide conversation
    """
    logger.debug('intent={}'.format(intent_request['currentIntent']))
    logger.debug('session={}'.format(intent_request['sessionAttributes']))
    slots = intent_request['currentIntent']['slots']

    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}

    msg = 'Session is empty'
    if ( len(session_attributes.keys() )):
        msg = 'Session contains '
        for key in session_attributes:
            msg += key + ','



    # create the response message
    logger.debug('session_details msg={}'.format(msg))
    
    return close(
        session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': msg
        }
    )

def fluid_level(intent_request):
    """
    Performs dialog management for retrieving wellsite production stats.

    Beyond data retrieval, the implementation for this intent demonstrates the following:
    1) Use of elicitSlot in slot validation and re-prompting
    2) Use of sessionAttributes to pass information that can be used to guide conversation
    """
    logger.debug('intent={}'.format(intent_request['currentIntent']))
    logger.debug('start session={}'.format(intent_request['sessionAttributes']))
    slots = intent_request['currentIntent']['slots']
    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}

    # extract wellsite slot value
    wellsite_id = ''
    
    if 'wellsiteId' in slots:
        wellsite_id = slots['wellsiteId']

    if not wellsite_id:
        logger.debug('wellsiteid is not specified.  retrieving from session')
        if 'wellsiteId' in session_attributes:
            wellsite_id = try_ex(lambda: session_attributes['wellsiteId'])


    # Validate our slot values.  If any are invalid, re-elicit for their value
    validation_result = validate_wellsiteid(wellsite_id)
    if validation_result['isValid']:
        session_attributes['wellsiteId'] = wellsite_id
    else:
        slots[validation_result['violatedSlot']] = None
        return elicit_slot(
            session_attributes,
            intent_request['currentIntent']['name'],
            slots,
            validation_result['violatedSlot'],
            validation_result['message']
        )


    # load the wellsite visit record
    wellsite_visit_record = retrieve_from_session(session_attributes, 'wellsiteVisitRecord')
        
    if not wellsite_visit_record or not wellsite_visit_record['wellSiteId'] == wellsite_id:
        logger.debug('could not find wellsite visit in session or mismatch on wellsite id.  looking in dynamo')
        wellsite_visit_record = retrieve_wellsite_visit_record(wellsite_id)

        
        if wellsite_visit_record is None:
            return elicit_slot(
                session_attributes,
                intent_request['currentIntent']['name'],
                slots,
                'wellsiteId',
                {'contentType': 'PlainText', 'content': 'Could not retrieve last visit details for wellsite {}.  Please try again.'.format(wellsite_id)}
            )
        session_attributes['wellsiteVisitRecord'] = json.dumps(wellsite_visit_record)
    



    # create the response message
    msg = '{} reported a fluid level of {} on {}'.format(wellsite_visit_record['fluidLevelCheckedBy'], wellsite_visit_record['fluidLevel'], wellsite_visit_record['fluidLevelCheckedDate'])
    logger.debug('production_stats msg={}'.format(msg))
    logger.debug('session={}'.format(session_attributes))
    
    return close(
        session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': msg
        }
    )

def rod_replacement(intent_request):
    """
    Performs dialog management for retrieving wellsite production stats.

    Beyond data retrieval, the implementation for this intent demonstrates the following:
    1) Use of elicitSlot in slot validation and re-prompting
    2) Use of sessionAttributes to pass information that can be used to guide conversation
    """
    logger.debug('intent={}'.format(intent_request['currentIntent']))
    logger.debug('start session={}'.format(intent_request['sessionAttributes']))
    slots = intent_request['currentIntent']['slots']
    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}

    # extract wellsite slot value
    wellsite_id = ''
    
    if 'wellsiteId' in slots:
        wellsite_id = slots['wellsiteId']

    if not wellsite_id:
        logger.debug('wellsiteid is not specified.  retrieving from session')
        if 'wellsiteId' in session_attributes:
            wellsite_id = try_ex(lambda: session_attributes['wellsiteId'])


    # Validate our slot values.  If any are invalid, re-elicit for their value
    validation_result = validate_wellsiteid(wellsite_id)
    if validation_result['isValid']:
        session_attributes['wellsiteId'] = wellsite_id
    else:
        slots[validation_result['violatedSlot']] = None
        return elicit_slot(
            session_attributes,
            intent_request['currentIntent']['name'],
            slots,
            validation_result['violatedSlot'],
            validation_result['message']
        )


    # load the wellsite visit record
    wellsite_visit_record = retrieve_from_session(session_attributes, 'wellsiteVisitRecord')
        
    if not wellsite_visit_record or not wellsite_visit_record['wellSiteId'] == wellsite_id:
        logger.debug('could not find wellsite visit in session or mismatch on wellsite id.  looking in dynamo')
        wellsite_visit_record = retrieve_wellsite_visit_record(wellsite_id)

        
        if wellsite_visit_record is None:
            return elicit_slot(
                session_attributes,
                intent_request['currentIntent']['name'],
                slots,
                'wellsiteId',
                {'contentType': 'PlainText', 'content': 'Could not retrieve last visit details for wellsite {}.  Please try again.'.format(wellsite_id)}
            )
        session_attributes['wellsiteVisitRecord'] = json.dumps(wellsite_visit_record)
    

    # create the response message
    msg = '{} replaced the rod on {}'.format(wellsite_visit_record['rodReplacedBy'], wellsite_visit_record['rodReplacementDate'], wellsite_visit_record['fluidLevelCheckedDate'])
    logger.debug('production_stats msg={}'.format(msg))
    logger.debug('session={}'.format(session_attributes))
    
    return close(
        session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': msg
        }
    )


def comments(intent_request):
    """
    Performs dialog management for retrieving wellsite production stats.

    Beyond data retrieval, the implementation for this intent demonstrates the following:
    1) Use of elicitSlot in slot validation and re-prompting
    2) Use of sessionAttributes to pass information that can be used to guide conversation
    """
    logger.debug('intent={}'.format(intent_request['currentIntent']))
    logger.debug('start session={}'.format(intent_request['sessionAttributes']))
    slots = intent_request['currentIntent']['slots']
    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}

    # extract wellsite slot value
    wellsite_id = ''
    
    if 'wellsiteId' in slots:
        wellsite_id = slots['wellsiteId']

    if not wellsite_id:
        logger.debug('wellsiteid is not specified.  retrieving from session')
        if 'wellsiteId' in session_attributes:
            wellsite_id = try_ex(lambda: session_attributes['wellsiteId'])


    # Validate our slot values.  If any are invalid, re-elicit for their value
    validation_result = validate_wellsiteid(wellsite_id)
    if validation_result['isValid']:
        session_attributes['wellsiteId'] = wellsite_id
    else:
        slots[validation_result['violatedSlot']] = None
        return elicit_slot(
            session_attributes,
            intent_request['currentIntent']['name'],
            slots,
            validation_result['violatedSlot'],
            validation_result['message']
        )


    # load the wellsite visit record
    wellsite_visit_record = retrieve_from_session(session_attributes, 'wellsiteVisitRecord')
        
    if not wellsite_visit_record or not wellsite_visit_record['wellSiteId'] == wellsite_id:
        logger.debug('could not find wellsite visit in session or mismatch on wellsite id.  looking in dynamo')
        wellsite_visit_record = retrieve_wellsite_visit_record(wellsite_id)

        
        if wellsite_visit_record is None:
            return elicit_slot(
                session_attributes,
                intent_request['currentIntent']['name'],
                slots,
                'wellsiteId',
                {'contentType': 'PlainText', 'content': 'Could not retrieve last visit details for wellsite {}.  Please try again.'.format(wellsite_id)}
            )
        session_attributes['wellsiteVisitRecord'] = json.dumps(wellsite_visit_record)
    

    # create the response message
    msg = 'the well was visited on {} and operator commented {}'.format(wellsite_visit_record['dateOfLastVisit'], wellsite_visit_record['comments'] )
    logger.debug('production_stats msg={}'.format(msg))
    logger.debug('session={}'.format(session_attributes))
    
    return close(
        session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': msg
        }
    )

def new_wellsite_visit_record(wellsiteId):
    wellsite_visit_record = {
        'wellSiteId': wellsiteId,
        'rodCondition': ' ',
        'rodReplacementDate': ' ',
        'rodReplacedBy': ' ',
        'fluidLevel': ' ',
        'fluidLevelCheckedDate': ' ',
        'fluidLevelCheckedBy': ' ',
        'dateOfLastVisit': ' ',
        'durationOfLastVisit': ' ',
        'comments': ' '
    }
    return wellsite_visit_record
    


def wellsite_visit(intent_request):
    """
    Performs dialog management for retrieving wellsite production stats.

    Beyond data retrieval, the implementation for this intent demonstrates the following:
    1) Use of elicitSlot in slot validation and re-prompting
    2) Use of sessionAttributes to pass information that can be used to guide conversation
    """
    logger.debug('intent={}'.format(intent_request['currentIntent']))
    logger.debug('start session={}'.format(intent_request['sessionAttributes']))
    slots = intent_request['currentIntent']['slots']
    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}

    # extract wellsite slot value
    wellsite_id = ''
    
    if 'wellsiteId' in slots:
        wellsite_id = slots['wellsiteId']

    if not wellsite_id:
        logger.debug('wellsiteid is not specified.  retrieving from session')
        if 'wellsiteId' in session_attributes:
            wellsite_id = try_ex(lambda: session_attributes['wellsiteId'])


    # Validate our slot values.  If any are invalid, re-elicit for their value
    validation_result = validate_wellsiteid(wellsite_id)
    if validation_result['isValid']:
        session_attributes['wellsiteId'] = wellsite_id
    else:
        slots[validation_result['violatedSlot']] = None
        return elicit_slot(
            session_attributes,
            intent_request['currentIntent']['name'],
            slots,
            validation_result['violatedSlot'],
            validation_result['message']
        )

    # confirm this is a valid well by retrieving record from the DB
    wellsite_location_record = retrieve_from_session(session_attributes, 'wellsiteLocationRecord')
    
    if not wellsite_location_record or not wellsite_location_record['wellSiteId'] == wellsite_id:
        logger.debug('could not find wellsite record in session or mismatch on wellsite id')
        wellsite_location_record = retrieve_wellsite_location_record(wellsite_id)
    
        if wellsite_location_record is None:
            return elicit_slot(
                session_attributes,
                intent_request['currentIntent']['name'],
                slots,
                'wellsiteId',
                {'contentType': 'PlainText', 'content': 'Could not retrieve details of wellsite {}.  Please try again.'.format(wellsite_id)}
            )
        session_attributes['wellsiteLocationRecord'] = json.dumps(wellsite_location_record)


    # extract and validate each slot
    operator_name = slots['operatorName']
    time_on_site = slots['timeOnSite']
    rod_condition = slots['rodCondition']
    fluid_level = slots['fluidLevel']
    curTimestamp = '2019-02-02 2:02:02'

    # create a new wellsite visit record
    wellsite_visit_record = new_wellsite_visit_record(wellsite_id)
    wellsite_visit_record['rodCondition'] = rod_condition
    wellsite_visit_record['rodReplacementDate'] = ' '
    wellsite_visit_record['rodReplacedBy'] = ' '
    wellsite_visit_record['fluidLevel'] = fluid_level
    wellsite_visit_record['fluidLevelCheckedDate'] = curTimestamp
    wellsite_visit_record['fluidLevelCheckedBy'] = operator_name
    wellsite_visit_record['dateOfLastVisit'] = curTimestamp
    wellsite_visit_record['durationOfLastVisit'] = time_on_site
    wellsite_visit_record['comments'] = ' '
    addWellsiteVisitRecordToDynamo(wellsite_visit_record)
    session_attributes['wellsiteVisitRecord'] = json.dumps(wellsite_visit_record)
    

    # create the response message
    msg = 'thank-you {} the information has been saved'.format(operator_name)
    logger.debug('production_stats msg={}'.format(msg))
    logger.debug('session={}'.format(session_attributes))
    
    return close(
        session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': msg
        }
    )
# --- Intents ---


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'GetProductionStats':
        return production_stats(intent_request)
    elif intent_name == 'GetSessionDetails':
        return session_details(intent_request)
    elif intent_name == 'GetFluidLevel':
        return fluid_level(intent_request)
    elif intent_name == 'GetRodReplacement':
        return rod_replacement(intent_request)
    elif intent_name == 'GetComments':
        return comments(intent_request)
    elif intent_name == 'WellsiteVisit':
        return wellsite_visit(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')


# --- Main handler ---


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/Edmonton time zone.
    os.environ['TZ'] = 'America/Edmonton'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)
