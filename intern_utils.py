from pymongo import MongoClient
from slackclient import SlackClient
import os
import json

# TODO: maybe refactor to make it a class, also generally don't do redundant connections,
# TODO: serialize the object when you pull and check for updates every 2 mins or something and update if changes

# I think I should pass in a database connection or something to all of these ... , db)

# TODO: figure out what makes the most sense to return


class Person():
    def __init__(self, name, points_to_award=100, has_awarding_privileges=True ):
        # type: (str, float, bool) -> object
        self.name = name
        self.points_to_award = points_to_award
        self.awarding_privileges = has_awarding_privileges
        self.user_id = ""

    def replenish(self, points=100):
        self.points_to_award = points

    def check_awarding_privileges(self):
        return self.awarding_privileges

    def award_points(self, intern, amount):
        # type: (Person, Intern) -> None
        # should probably return some info maybe like in a string
        if self.points_to_award >= amount > 0:
            self.points_to_award -= amount
            intern.add_points(amount)
        else:
            pass


class Intern(Person):
    def __init__(self, name, points=0):
        self.points = 0
        super(Intern, self).__init__(name)

    def add_points(self, points):
        # type: (float) -> object
        assert isinstance(points, float)
        self.points += points


class Matt(Intern):
    def __init__(self):
        super(Matt, self).__init__("Matt")

    @staticmethod #maybe, but possibly not
    def revoke_awarding_privileges(person):
        person.awarding_privileges = False

    @staticmethod
    def grant_awarding_privilege(person):
        person.awarding_privileges = False
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


if __name__ == "__main__":
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        initialize()



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