import os
import time
from slackclient import SlackClient
from pymongo import MongoClient
from intern_utils import *

# make mongo client
mongo_client = MongoClient('localhost', 34567)
db = mongo_client.pymongo_test
interns = db.interns
"""
interns_data = {
    'name': 'matt',
    'points': 1000
}
result = interns.insert_one(interns_data)
print('One post: {0}'.format(result.inserted_id))
interns_data = {
    'name': 'jimmy',
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


def get_about():
    print "about"
    return "intern.rank is a bot created by the interns to haze themselves. Try typing '@intern.rank' help to get " \
           "started "

def get_status():
    print "status called"

    #get top spot
    top=interns.find().sort("points", -1)[0]
    name = top["name"]
    points = top["points"]

    return "The current leader is "+name+", with "+str(points)+"."


def update_rank():
    print "update rank called"
    iter=0
    response=""
    #sort in ascending order or something
    for intern in interns.find().sort("points", -1):
        iter+=1

        response+=str(iter)+". "+intern["name"] +"\t"+str(intern["points"]) + "\n"
        print intern["points"]

    return response


def get_rankings():
    print "rankings called"
    response= update_rank()

    return response #"Who even cares, Matt is going to win."


def add_points(command, sender):
    # TODO: change this to be not 3 calls
    print "points called"
    assert command[0] == "points"

    name, points_to_add = command[1],float(command[2])

    if check_awarding_privileges(sender):
        awarder = employees.find_one({"userID":sender})
        awarders_points = float(awarder["awarding_points"])
        awarder_name = awarder["name"]

        if awarders_points <= points_to_add:
            return "Sorry, you can\'t award {0} points, you only have {1}. Points replenish on Monday.".format(
                str(points_to_add), str(awarders_points))

        if name == "matt" and points_to_add<0:
            return "You can't take points away from Matt!"

        old_points=interns.find_one({"name" : name})["points"]
        new_points= old_points+points_to_add
        interns.find_one_and_update( {"name" : name}, {"$set":{"points": new_points}})

        new_awarders_points = awarders_points - points_to_add
        employees.find_one_and_update( {"userID" : sender}, {"$set":{"awarding_points": new_awarders_points}})

        response = str(points_to_add) + " points to "+name + "! " + name + " now has " + str(new_points) + " points. \n"
        response += awarder_name + " has " + str(new_awarders_points) + " left to award for the week."

        return response

    else:
        return "Sorry, you can't award points."


def get_intern():
    print "intern called"

    if round(time.time())%2==0:
        return "The super special intern is Matt right now."

    return "The super special intern is Jimmy right now."


def get_help():
    print "help called"
    response = "Use the the format '@intern.rank + <<command>>' and try one of the following commands:\n"
    response+="about\nintern\nJimmy\nMatt\n"
    response+="points <<intern_name>> <<number of points to add>> \n"
    response+="rankings\nstatus"
    return response


def get_Matt():
    # these functions are really dumb idk
    print "Matt called"

    return "@matt.nicholson I think someone wants to talk to you"


def get_Jimmy():
    # these functions are dumb
    print "Jimmy called"
    bankrupt("jimmy") # lol

    return "@jimmycarlson I think someone wants to talk to you"


def handle_command(command, channel, sender):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    command = command.split(" ")

    if command[0] == "status":
        response = get_status()

    elif command[0] == "rankings":
        response = get_rankings()

    elif command[0] == "points":
        response = add_points(command, sender)

    elif command[0] == "intern":
        response = get_intern()

    elif command[0] == "help":
        response = get_help()

    elif command[0] == "matt":
        response = get_Matt()

    elif command[0] == "jimmy":
        response = get_Jimmy()

    elif command[0] == "about":
        response = get_about()

    else:
        response="Sorry, I didn't quite catch that. Type @intern.rank help for more options"

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
                return output['text'].split(AT_BOT)[1].strip().lower(), output['channel'], output_list[0]["user"]
    return None, None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1  # 1 second delay between reading from firehose

    if slack_client.rtm_connect():
        print("StarterBot connected and running!")

        while True:
            command, channel, sender = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                print "command detected " + str(command) + "\n"
                handle_command(command, channel, sender)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")

