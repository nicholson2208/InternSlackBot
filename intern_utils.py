from pymongo import MongoClient
from slackclient import SlackClient
import os

# TODO: maybe refactor to make it a class, also generally don't do redundant connections

# I think I should pass in a database connection or something to all of these ... , db)

# make mongo client
mongo_client = MongoClient('localhost', 34567)
db =mongo_client.pymongo_test
interns = db.interns
employees = db.employees

# intern.rank's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "points"

# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))


def add_intern(intern_name, points):
    data = dict(name=intern_name, points= points)

    interns.insert_one(data)


def delete_intern(intern_name):
    pass


def bankrupt(intern_name):
    pass


def get_users(slack_client):
    users = slack_client.api_call("users.list")
    assert users["ok"]

    return users["members"]


def add_users(user_list):
    # something about updating mongodb here and initializing the amount of points
    # they can give out

    # add to mongodb here

    for user in user_list:
        name=user["name"]
        user_id=user["id"]
        points = 100
        result = employees.insert_one(
            {'name': name, 'userID': user_id, 'awarding_points': points, 'has_awarding_privileges': True})
        print result


def replenish_awarding_points(user_name):
    employees.find_one_and_update({"name": user_name}, {"$set": {"points": 100}})
    print user_name + " points replenished."


def check_awarding_privileges(user_id):
    return employees.find_one({"userID" : user_id})["has_awarding_privileges"]


def revoke_awarding_privileges(user_name):
    # this param might be easier if it's user id
    employees.find_one_and_update({"name": user_name}, {"$set": {"has_awarding_privileges": False}})


def grant_awarding_privileges(user_name):
    employees.find_one_and_update({"name": user_name}, {"$set": {"has_awarding_privileges": True}})


def initialize():
    print "initializing"
    db.employees.delete_many({})
    db.interns.delete_many({})
    users = get_users(slack_client)
    add_users(users)

    add_intern("matt", 0)
    add_intern("jimmy", 0)

"""
if __name__ == "__main__":
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        initialize()
"""


"""
an intern looks like this:
{
    'name': 'matt',
    'points': 1000
}

a user looks like this:
{
    'name': 'ben',
    'userID': 'UXXXXXXXX',
    'awarding_points': 100,
    'has_awarding_privileges': True
}
"""