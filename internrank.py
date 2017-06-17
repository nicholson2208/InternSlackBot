import os
import time
from slackclient import SlackClient
from pymongo import MongoClient

#make mongo client
mongo_client = MongoClient('localhost', 23456)
db =mongo_client.pymongo_test
interns = db.interns
"""
interns_data = {
    'name': 'matt',
    'rank': 1,
    'points': 1000
}
result = interns.insert_one(interns_data)
print('One post: {0}'.format(result.inserted_id))
interns_data = {
    'name': 'jimmy',
    'rank': 2,
    'points': 100
}
result1 = interns.insert_one(interns_data)
print('One post: {0}'.format(result1.inserted_id))
"""

# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "points"

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))


def get_status():
    print "status called"

    #get top spot

    return "The current leader is "+name+", with "+str(points)+"."

def update_rank():
    print "update rank called"
    #sort in ascending order or something
    pass

def get_rank():
    print "rank called"
    update_rank()

    #print out the power rankings

    return "Who even cares, Matt is going to win."

def add_points(command):
    print "points called"
    assert command[0] == "points"
    name, points_to_add = command[1],command[2]
    print "the name is "+name
    if name =="matt" and points_to_add<0:
        print "You can't take points away from Matt!"
    old_points=interns.find_one({"name" : name})["points"]

    new_points= old_points+float(points_to_add)
    interns.find_one_and_update( {"name" : name}, {"$set":{"points": new_points}})

    return points_to_add + " points to "+name +"! "+name+" now has "+ str(new_points) +" points."


def get_intern():
    print "intern called"

    if round(time.time())%2==0:
        return "The super special intern is Matt right now."

    return "The super special intern is Jimmy right now."

def get_help():
    print "help called"
    response = "Use the the format '@intern.rank + <<command>>' and try one of the following commands:\n"
    response+="intern\nJimmy\nMatt\n"
    response+="points <<intern_name>> <<number of points to add>> \n"
    response+="rank\nstatus"
    return response

def get_Matt():
    print "Matt called"

    return "@matt.nicholson I think someone wants to talk to you"

def get_Jimmy():
    print "Jimmy called"
    return "@jimmycarlson I think someone wants to talk to you"

def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    command=command.split(" ")
    print "len " + str(len(command))

    if command[0] == "status":
        response=get_status()

    elif command[0] == "rank":
        response=get_rank()
    elif command[0] == "points":
        response=add_points(command)
        
    elif command[0] == "intern":
        response=get_intern()

    elif command[0]=="help":
        response=get_help()

    elif command[0] =="matt":
        response=get_Matt()

    elif command[0] =="jimmy":
        response=get_Jimmy()

    else:
        response="Sorry, I didn't quite catch that. Type @intern.rank help for more options"
        
    #response = "Matt gets 1000 points!"
    print response
    slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
 #   handle_command("help", True)

    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                print "command detected " + str(command) + "\n"
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
