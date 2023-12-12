import pymongo
from datetime import datetime, timezone
import re
import math
from bson.objectid import ObjectId

def connect_to_mongo(port):
    # Connect to MongoDB server
    client = pymongo.MongoClient(f"mongodb://localhost:{port}/")
    
    # Create or get the database
    db = client["291db"]

    return db

def search_tweets(db):
    searching = True
    while searching:
        kw_input = input("Enter one or more keywords: ")
        kw = [keyword.strip() for keyword in kw_input.split(',')]
        
        # Use re.escape to escape special characters (#) in keywords
        escaped_keywords = [re.escape(keyword) if not keyword.startswith('#') else '#' + re.escape(keyword[1:]) for keyword in kw]
        
        # Use \b for word boundaries in the regex
        r_query = [{"content": {"$regex": fr"\b{escaped_keyword}\b", "$options": "i"}} for escaped_keyword in escaped_keywords]
        query = {"$and": r_query}
        
        cursor = db["tweets"].find(query)
        tweet_counter = 1
        for document in cursor:
            username = document.get('user', {}).get('username', None)
            print("\nTweet", tweet_counter)
            print(f"ID: {document['id']}\nDate: {document['date']}\nContent: {document['content']}\nUsername: {username}\n")
            tweet_counter += 1

        while True:
            print("Menu:")
            print("1: Select a tweet for more info")
            print("2: Search different keywords")
            print("3: Return to home screen")
            user_choice = input("Pick an option (1, 2, or 3): ")

            if user_choice == '1':
                # Prompt the user to select a tweet for more info
                selected_tweet_number = input("Enter the tweet number you want to view in detail (or enter -1 to return to home screen): ")

                if selected_tweet_number.lower() == '-1':
                    searching = False
                    break

                try:
                    selected_tweet_number = int(selected_tweet_number)
                except ValueError:
                    print("Invalid input.")
                    continue

                # Reset the cursor and iterate to the selected tweet number
                cursor.rewind()
                for i, document in enumerate(cursor):
                    if i + 1 == selected_tweet_number:
                        # Display detailed information for the selected tweet
                        print(f"\nSelected Tweet:\nID: {document['id']}\nURL: {document['url']}\nDate: {document['date']}\nContent: {document['content']}\nRenderedContent: {document['renderedContent']}\
                        \nUsername: {username}\nOutlinks: {document['outlinks']}\ntcoOutlinks: {document['tcooutlinks']}\nNumber of Replies: {document['replyCount']}\
                        \nNumber of Retweets: {document['retweetCount']}\nNumber of Likes: {document['likeCount']}\nNumber of Quotes: {document['quoteCount']}\nConversationID: {document['conversationId']}\
                        \nLanguage: {document['lang']}\nSource: {document['source']}\nSource URL: {document['sourceUrl']}\nSource Label: {document['sourceLabel']}\nMedia: {document['media']}\
                        \nRetweeted Tweet: {document['retweetedTweet']}\nQuoted Tweet: {document['quotedTweet']}\nMentioned Users: {document['mentionedUsers']}\n")
                        break
                searching = False
            elif user_choice == '2':
                # Allow the user to search for different keywords
                searching = True
                break
            elif user_choice == '3':
                # Exit the search_tweets function
                searching = False
                break
            else:
                print("Invalid choice. Please enter a valid option (1-3).")

            

def search_users(db):
    keyword = input("Enter a keyword to search for users:")
    # The user should be able to provide a keyword
    # and see all users whose displayname or location contain the keyword.
    result = db.tweets.aggregate([
        {
            "$match": {
                "$or": [
                    {"user.displayname": {"$regex": fr"\b{keyword}\b", "$options": "i"}},
                    {"user.location": {"$regex": fr"\b{keyword}\b", "$options": "i"}}
                ]
            }
        },
        {
            "$group": {
                "_id": "$user.id",
                "username": {"$first": "$user.username"},
                "displayname": {"$first": "$user.displayname"},
                "location": {"$first": "$user.location"},
                "userid": {"$first": "$user.id"}
            }
        }
    ])
    results = []
    for user in result:
        results.append(user)
    return results

def choice2(db):
    result = search_users(db)
    for i in range(len(list(result))):
        try:
            print(f'***\n{i+1}. Username: {result[i]["username"]}\nDisplayname: {result[i]["displayname"]}\nLocation: {result[i]["location"]}')
        except:
            print("***End of results***")
            end = True
            break
    selecting = True
    while selecting:
        print("")
        print("1. Select a user\n2. Exit user search\n")
        response = input("Enter your choice: ")
        print("")
        if response == "1":
            valid = False
            exited = False
            while not valid:
                try:
                    selection = int(input("Enter the number of the user you would like to select or any non-number character to exit: "))
                    print("")
                    if selection > len(result):
                            print("Invalid input; please select a user from the current page\n")
                    else:
                        select(result[selection - 1]["userid"], db)
                        valid = True
                except:
                    exited = True
                    break
        elif response == "2":
            selecting = False            
        else:
            print("Invalid input")

def select(userid, db):
    collection = db["tweets"]
    result = collection.find({"user.id": userid})
    results = []
    max = 0
    for r in result:
        results.append(r)
    if len(results) > 1: 
        for i in range(len(results)):
            if results[i]["user"]["followersCount"] > results[max]["user"]["followersCount"]:
                max = i
    print(results[max]["user"])

def list_top_tweets(db):
    print("function list_top_tweets")
    print("1. List top tweets by number of retweetCount")
    print("2. List top tweets by number of likeCount")
    print("3. List top tweets by number of quoteCount")

    type_choice = input("Enter your choice (1-3): ")
    while not type_choice.isdigit() or int(type_choice) not in range(1, 4):
        print("Invalid choice. Please try again.")
        type_choice = input("Enter your choice (1-3) again: ")
    type_choice = int(type_choice)

    print("how many top tweets do you want to list? Please enter a number")
    num_choice = input("Enter your choice: ")
    while not num_choice.isdigit():
        print("Invalid choice. Please try again.")
        num_choice = input("Enter your choice again: ")
    num_choice = int(num_choice)

    # The result will be ordered in a descending order of the selected field. 
    # For each matching tweet, display the id, date, content, and username of
    # the person who posted it. The user should be able to select a tweet and see all fields.

    if type_choice == 1:
        print("\nlist top {} tweets by number of retweetCount".format(num_choice))
        tweets = db["tweets"].find().sort("retweetCount", -1).limit(num_choice)
        print_top_tweets_info(tweets, type_choice)

    elif type_choice == 2:
        print("\nlist top {} tweets by number of likeCount".format(num_choice))
        tweets = db["tweets"].find().sort("likeCount", -1).limit(num_choice)
        print_top_tweets_info(tweets, type_choice)

    elif type_choice == 3:
        print("\nlist top {} tweets by number of quoteCount".format(num_choice))
        tweets = db["tweets"].find().sort("quoteCount", -1).limit(num_choice)
        print_top_tweets_info(tweets, type_choice)
    
    tweet_id = input("Enter the id of the tweet you want to see all fields, or enter 'quit' to quit: \n")
    if tweet_id.lower() == "quit" or tweet_id.lower() == "q":
        return
    else:
        select_tweet = db["tweets"].find_one({"_id": ObjectId(tweet_id)})
        while select_tweet == None:
            print("Invalid tweet id. There is no tweet to display.")
            tweet_id = input("Enter the id of the tweet you want to see all fields again, or enter 'quit' to quit: \n")
            if tweet_id.lower() == "quit" or tweet_id.lower() == "q":
                break
        if select_tweet != None:
            print("\nHere are all fields of the tweet with id {}: ".format(tweet_id))
            print(select_tweet)

def print_top_tweets_info(tweets, type_choice):
    for tweet in tweets:
            print("")
            print("oid:", tweet.get("_id"))
            print("date:", tweet.get("date"))
            print("content:", tweet.get("content"))
            print("username:", tweet.get("user").get("username"))
            if type_choice == 1:
                print("retweetCount:", tweet.get("retweetCount"))
            elif type_choice == 2:
                print("likeCount:", tweet.get("likeCount"))
            elif type_choice == 3:
                print("quoteCount:", tweet.get("quoteCount"))
            print("")




def list_top_users(db):
    value = True
    while value == True:
        try:
            tweets_count = int(input("Provide numb of users you would like to see based on followers count: "))
            value = False
        except:
            print("Invalid Input, Try again\n")
    pipeline = [
        {
            "$group": {
                "_id": "$user.username",
                "maxFollowersCount": { "$max": "$user.followersCount" },
                "displayname": { "$first": "$user.displayname" }
            }
        },
        {
            "$project": {
                "_id": 0,
                "username": "$_id",
                "displayname": "$displayname",
                "followersCount": "$maxFollowersCount"
            }
        },
        {
            "$sort": {"followersCount": -1}
        },
        {
            "$limit": tweets_count
        }
    ]    
    results = db["tweets"].aggregate(pipeline)
    print_top_users(db, list(results))
    
    return
    
            
            

def print_top_users(db, results):
    n = 1
    value = True
    names = []    
    for dicts in results:
        names.append(dicts['username'])
        print(f"{n} username: {dicts['username']}  displayname: {dicts['displayname']}  followersCount: {dicts['followersCount']}\n")
        n+=1
    user_input = input(f"Please select from 1 - {n-1} to see more information or -1 to return back: ")
    while user_input.isalpha() or (int(user_input) not in range(1, n ) and int(user_input) != -1):
            print("Invalid Entry,  try again")
            user_input = input(f"Please select from 1 - {n-1} to see more information or -1 to return back: ")
        
    if user_input == -1:
        return
    else :
        ############call noisyforever function with username:
        result = db["tweets"].aggregate([{"$match": {"user.username": {"$regex": names[int(user_input)-1]}}}])
        user_dict = list(result)[0]
        uid = user_dict.get('user').get('id')
        select(uid, db)
        return

def set_tweet(create_dict, found_tweet):
    for key,values in found_tweet.items():
        if isinstance(values,dict):
            set_tweet(create_dict,values)
        elif key not in create_dict.keys():
            found_tweet[key] = None    
        elif key in create_dict.keys():
            found_tweet[key] = create_dict[key]
    return found_tweet
def compose_tweet(db):
    current_utc_time = datetime.now(timezone.utc)
    current_date = current_utc_time.strftime('%Y-%m-%dT%H:%M:%S%z')    
    user_input = str(input("Please enter a tweet you would like to compose: "))
    create_dict = {"date":current_date,"content":user_input,"username":"291user"}
    found_tweet = db['tweets'].find_one()
    found_tweet.pop('_id')
    tweet = set_tweet(create_dict,found_tweet)
    db['tweets'].insert_one(tweet)
    print("Tweet has been composed sucessfully\n")
    user_ask = str(input("Would you like to compose another tweet(y/n): ")).lower()
    if user_ask == 'y':
        compose_tweet(db)
    else:
        return
def main():
    port = input("Enter port number: ")
    while not port.isdigit():
        print("Invalid port number. Please try again.")
        port = input("Enter port number again: ")
    port = int(port)
    # port = 61288

    db = connect_to_mongo(port)

    while True:
        print("\nMain menu")
        print("1. Search for tweets ")
        print("2. Search for users ")
        print("3. List top tweets ")
        print("4. List top users ")
        print("5. Compose a tweet ")
        print("6. Exit ")

        choice = input("Enter your choice (1-6): ")
        while not choice.isdigit() or int(choice) not in range(1, 7):
            print("Invalid choice. Please try again.")
            choice = input("Enter your choice (1-6): ")
        choice = int(choice)

        if choice == 1:
            search_tweets(db)
        elif choice == 2:
            choice2(db)
        elif choice == 3:
            list_top_tweets(db)
        elif choice == 4:
            list_top_users(db)
        elif choice == 5:
            compose_tweet(db)
        elif choice == 6:
            print("Exit the program, Goodbye!")
            break

if __name__ == "__main__":
    main()
