
#TODO: maybe refactor to make it a class, also generally don't do redundant connections

#I think I should pass in a database connection or something to all of these ... , db)

def add_intern(intern_name, points):
    pass

def delete_intern(intern_name):
    pass

def bankrupt(intern_name):
    pass

def get_users(slack_client):
    return slack_client.api_call("users.list")

def add_users(user_list):
    #something about updating mongodb here and intializing the amount of points
    #they can give out
    for user in user_list:
        pass
    pass

def replenish_awarding_points(user_name, points):
    pass

def revoke_awarding_privileges(user_name):
    pass

def grant_awarding_privileges(user_name):
    pass

"""
an intern looks like this:
{
    'name': 'matt',
    'points': 1000
}

a user looks like this:
{
    'name': 'ben',
    'awarding_points': 100,
    'has_awarding_privileges': True
}
"""