#!/usr/bin/env python
# coding: utf-8

#Author's notes: Takes about 45 mins to run in worst case... please be patient

import twitter
#Defining parameters for Open authentication to use Twitter API
CONSUMER_KEY = "foeSLqcNNI1V9tsIdindiD5Fa"
CONSUMER_SECRET = "8kkwiKdC3Jb9I5mgSaMMy3B4wb0O2NOhmH0lwrIPFK5RPDmnjr"
OAUTH_TOKEN = "2181898994-ZEFxxuz01wXaNzc68LEXjVOkqz3EokYJjwSFx7S"
OAUTH_SECRET = "8Q0PhWTh8K3t6DU85uZYZgAQHI9LcyTQJFnViI4Bwl0A4"

auth = twitter.oauth.OAuth(OAUTH_TOKEN,OAUTH_SECRET,CONSUMER_KEY, CONSUMER_SECRET)
#Creating Twoitter API object to make all future calls to fetch data
twitter_api = twitter.Twitter(auth=auth)

#print(twitter_api.users.lookup(screen_name = "edmundyu1001"))

import sys
import time
from urllib.error import URLError
from http.client import BadStatusLine

#ERROR Handling by passing twitter function and list of all positional and keyword parameters
def twitter_func_call(twitter_func, max_errors =10, *args, **kwargs):
    
    #Handling errors based on cookbook functions
    def handle_errors(error, wait_time = 10):
        #Error Descriptions are self explanatory
        if error.e.code == 401:
            print('Not Authorized to view.', file=sys.stderr)
            return None
        elif error.e.code == 403:
            print('Request is understood but refused.', file=sys.stderr)
            return None
        elif error.e.code == 404:
            print('Typical 404 Not found.', file=sys.stderr)
            return None
        elif error.e.code == 429:
            print('Calm down. Rate limit reached. Waiting for 15 min window to pass...', file=sys.stderr)
            time.sleep(903)
            print('Continuing again')
            return wait_time
        elif error.e.code in (500,502,503,504):
            print('Not your fault. Twitter is going bananas with request or is down or something else. Retry in a while.')
            return wait_time
        else:
            raise error
            
    error_count = 0
    wait_time = 1

    while True:
        try:
            return twitter_func(*args, **kwargs)
        #Handles actual Twitter_api related errors on runtime
        except twitter.api.TwitterHTTPError as error:
            error_count = 0 
            wait_time = handle_errors(error,wait_time)
            if wait_time is None:
                return
        #Handles URL errors
        except URLError as e:
            error_count += 1
            time.sleep(wait_time)
            print("URLError encountered. Continuing.", file=sys.stderr)
            if error_count > max_errors:
                print("Too many consecutive errors...bailing out.", file=sys.stderr)
                raise
        #Handles communication errors
        except BadStatusLine as e:
            error_count += 1
            time.sleep(wait_time)
            print("BadStatusLine encountered. Continuing.", file=sys.stderr)
            if error_count > max_errors:
                print("Too many consecutive errors...bailing out.", file=sys.stderr)
                raise
        
#twitter_api.users.lookup(screen_name = "edmundyu1001")
#print(json.dumps(twitter_func_call(twitter_api.users.lookup,screen_name = "edmundyu1001"),indent=2))

#Collects alist of top 5 reciprocal friends based on Popularity ie Follower count
def collect_top_5_reciprocal_friends(user_id = 165035772,max_count =5000):
    friends = twitter_api.friends.ids(user_id = user_id,count = max_count)#Call 1
    followers = twitter_api.followers.ids(user_id = user_id,count = max_count)#Call 2
    print('Collected friends and followers for {0}, friends count : {1}, followers count: {2}'.format(user_id,len(friends["ids"]),len(followers["ids"])))
    #collect ids for all reciprocal friends
    reciprocal_friends_ids = list(set(friends["ids"])&set(followers["ids"]))
    #print(reciprocal_friends_ids)
    #Sort reciprocal friends based on their respective follower count
    top_5_reciprocal_friends = sorted(twitter_api.users.lookup(user_id=reciprocal_friends_ids), key = lambda x : x["followers_count"],reverse =True)
    #Call no_of reciprocal_friends / 100 for edmundyu1001 == 1
    top_5_reciprocal_friends_ids = []
    #Collect only 5 of the top friends. COuld have used list slicing, 
    #But, it gives error at a later stage when an id has no reciprocal friends. returns a Nonetype which is difficult to handle there.
    for index, user in enumerate(top_5_reciprocal_friends):
        top_5_reciprocal_friends_ids.append(user["id"])
        if index ==4:
            break;
    return top_5_reciprocal_friends_ids
#print(twitter_func_call(collect_top_5_reciprocal_friends,user_id = 165035772)) #edmundyu1001 = 165035772; MaitreyaSat = 2181898994

import networkx as nx
import matplotlib.pyplot as plt
Graph = nx.Graph()
#maintain a queue of users to be checked in the future and a list of all visited users
queue = []
start_point = 165035772 #Starting with edmundyu1001's profile.
queue.append(start_point)
#Dictionary to maintaina a list of users and their followers to save API calls again at a later stage, to create networkx graph.
dictionary = {}
index = 0
count = 0
while len(queue)<100 and index<len(queue):
    print('Queue:'+str(queue)+"\n"+"Users collected = "+str(len(queue)))
    print('Checking user: '+str(queue[index]))
    ids_to_check = twitter_func_call(collect_top_5_reciprocal_friends,user_id = queue[index])
    #the later phase that caused a none type error. Aargh!
    if ids_to_check is not None:
        print(ids_to_check)
        values = []
        #Add reciprocal fiends to queue if not already in queue and also not visited
        for curr_id in ids_to_check:
            values.append(curr_id)
            count+=1
            if(curr_id not in queue):
                queue.append(curr_id)
                
                
        #Also update the dictionary for every visited user
        dictionary[queue[index]]=values

    index+=1

#Create the graph only for the 100 users collected from dictionary to avoid additional API calls.
for k,v in dictionary.items():
    for x in v:
        Graph.add_edge(k,x)
        
        
#Distance Metrics using networkx package
diameter = nx.diameter(Graph)
avg_distance =nx.average_shortest_path_length(Graph)
print("Number of Nodes = "+ str(len(queue)))
print("Number of edges = "+str(count))
print("Diameter = "+ str(diameter))
print("Average Distance = "+str(avg_distance))


#Print and save the Graph
fig, ax = plt.subplots(1, 1, figsize=(16, 10));
nx.draw(Graph,with_labels = True,ax=ax,node_color = "Cyan")
mystr = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
'2009-01-05 22:14:39'
plt.savefig("SMDMA2-"+str(len(queue))+"-"+str(mystr)+".png", format="PNG")
plt.show()

# for k,v in dictionary.items():
#     for x in v:
#         if x in visited:
#             Graph.add_edge(k,x)
# fig, ax = plt.subplots(1, 1, figsize=(16, 16));
# nx.draw(Graph,with_labels = True,ax=ax,node_color = "Cyan")
# plt.savefig("Graph2.png", format="PNG")

