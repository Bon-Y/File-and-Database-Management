# MINI PROJECT 1: CMPUT 291
# -- This project is to build an application that keeps the enterprise data in a database
#    and to provide services to users.
# -- Code is entirely written in Python.
# -- Group Members' CCID: mekha, jkisilev, fanbang, bparkash


# Import modules
import sqlite3
import getpass
import random
import time
import subprocess as sp
import os.path
import math

connection = None
cursor = None
run = 1
index = -1

# for searching
global offset
offset = 0
more = 'y'
global keywords
keywords = []

################choice 5,6#################
def query_test():
    """
    Checking certain query tests for debugging purposes.
    
    """
    
    global connection, cursor
    

    try:
        cursor.execute('SELECT * from users') 
        
        data = cursor.fetchall()
        
    except sqlite3.Error as e:
        print(e)
    
    for i in range(len(data)):
        print(data[i])

    connection.commit()

def connect(path):
    '''
    This function is used to connect to the database
    '''
    global connection, cursor
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute(' PRAGMA forteign_keys=ON; ')
    connection.commit()
    return

def read_data():
    '''
    This function is used to read data from the files and insert into the database
    '''
    file_name = input("Database: ")
    file = open(file_name)
    file_data = file.read()
    file.close()
    

    global connection, cursor
    
    insert_query = file_data
    try:
        cursor.executescript(insert_query)
        connection.commit()
    except sqlite3.Error as e:
        print(e)

    print("SUCCESSFULLY INSERTED DATA \n")


def login_reg_screen():
    '''
    This function is used to display the login and registration screen
    '''
    global connection, cursor
    print("Welcome to index-instigators")
    print("1. Login -- use your user id and password")
    print("2. Register -- if you don't have an account")
    print("3. Exit")
    choice = input("Enter your choice: ")
    if choice == "1":
        result = login()
        return result
    elif choice == "2":
        return register()
    elif choice == "3":
        sp.run('clear', shell=True)
        print("Thank you for using index-instigators\n")
        connection.close()
        exit()
    else:
        print("Invalid choice")
        return login_reg_screen()

def login():
    '''
    This function is used to login the user
    '''
    global connection, cursor
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    
    cursor.execute("select * from users where usr = ? and pwd = ?", (username, password))
    result = cursor.fetchall()
    if len(result) == 0:
        print("Invalid username or password")
        return login_reg_screen()
    else:
        print("Login Successful")
        return ("Successful", result[0])


def print_tweet(result, index):
    # list_all helper function
    print("Tweet ID: ", result[index][0], "Writer: ", result[index][1], "Date: ", result[index][2])
    print("Text: ", result[index][3])
    print(" ")

def print_tweet_details():
    tweet_id = input("Enter tweet ID that you would like to see details: ")
    cursor.execute("select tid, writer, tdate, text, replyto from tweets where tid = ?", (tweet_id,))
    result2 = cursor.fetchall()
    if len(result2) == 0:
        print("Invalid tweet ID")
    else:
        cursor.execute("select count(*) from retweets where tid = ?", (tweet_id,))
        result3 = cursor.fetchall()
        cursor.execute("select count(*) from tweets where replyto = ?", (tweet_id,))
        result4 = cursor.fetchall()
        print("Tweet ID: ", result2[0][0], "Writer: ", result2[0][1], "Date: ", result2[0][2])
        print("Text: ", result2[0][3])
        print("Number of retweets: ", result3[0][0])
        print("Number of replies: ", result4[0][0])
        print(" ")

def print_retweet(result, index):
    print("Tweet ID: ", result[index][0], "Writer: ", result[index][2], "TweetDate: ", result[index][3])
    print("Text: ", result[index][4])
    print("ReTweetDate: ", result[index][1])
    print(" ")
################choice 1,2#################

################choice 5,6#################
def compose_tweet(usr: int, tweet: str, reply_to = None) -> None:    #what if user try to compose same tweet again
    '''
    This Function will update a tweet table and call helper function to update hashtag in mention and hashtag tables.
    '''
    global connection, cursor
    current_date = time.strftime("%Y-%m-%d")
    usr_id = (int(usr),)
    cursor.execute('SELECT name FROM users WHERE usr=?;', usr_id)
    usr_name = cursor.fetchone()
    cursor.execute('SELECT count(*) FROM tweets;')
    ID = cursor.fetchone()
    if len(ID) == 0:
        ID = 1
    else:
        ID = int(ID[0]) +1
        
    
    if len(usr_name) == 0:
        print("User does not exist")
        return False
    else:
        name = usr_name[0]
                
        cursor.execute(
        "INSERT INTO tweets VALUES (?, ?, ?, ?, ?);",
        (ID, int(usr), current_date, tweet,reply_to)
        )    
        Update_mention_hashtag(ID,usr,name,current_date,tweet)
        connection.commit()   
    return True

def Update_mention_hashtag(ID: int , usr: int,name: str,current_date: str,tweet: str) -> None:
    '''
    This function will update mention table and hastag table if i.e if exists any.
    Mltiple hashtags will also be updated in mention table. This function will call helper functions to update mentions and hastag table.
    '''
    global connection, cursor
    for i in range(len(tweet)):
        if tweet[i] == "#":
            hashtag = ""
            j = i+1
            while j <len(tweet) and (tweet[j] != " " and tweet[j] != "\n" and tweet[j] !="#"):
                hashtag += tweet[j]
                j+=1
            cursor.execute('SELECT term FROM hashtags WHERE term=?;', (hashtag,))
            term = cursor.fetchone()
            cursor.execute('SELECT * FROM mentions WHERE tid=? AND term=?;',(ID,hashtag))         #generally no need bcz Id will be diff everytime
            mention = cursor.fetchone()
            if term == None:
                Update_hashtag(hashtag)
            if mention == None:
                Update_mentions(ID,hashtag)
            i+= len(hashtag)
    return
def Update_hashtag(hashtag: str) -> None:
    '''
    This funtion will update hashtag table.
    '''
    global connection, cursor
    try:
        cursor.execute('INSERT INTO hashtags VALUES (?);', (hashtag,)) 
    except sqlite3.Error as e:
        print(e) 
    connection.commit()
    return
def Update_mentions(ID: int ,hashtag: str) -> None:
    '''
    This function will update mention table.
    '''
    global connection, cursor
    try:
        cursor.execute("INSERT INTO mentions VALUES (?, ?);",
        (ID, hashtag)
        )     
    except sqlite3.Error as e:
        print(e)  
    connection.commit()
    return

def list_followers(usr: str) ->None:
    '''
    This function will list all followers and provide more options to user to select.
    '''

    global connection, cursor
    flwee = (int(usr),)
    followers = []
    cursor.execute('SELECT flwer FROM follows WHERE flwee=?;', flwee)
    flwer = cursor.fetchall()
    if len(flwer) == 0:
        print("\nThere don't exist any followers\n")
        
    else:
        for i in range(len(flwer)):
            flwer_id  = (int(flwer[i][0]),)
            cursor.execute('SELECT name FROM users WHERE usr=?;', flwer_id)
            flwer_name = cursor.fetchone()
            followers.append(flwer_id[0])
            print(f"{i+1} {flwer[i][0]} {flwer_name[0]}")
        print("\n\n")
        user_input = input(f"Enter 1 - {len(flwer)} to view more information or enter -1 to go back: ")
        while user_input.isalpha() or (int(user_input) not in range(1, len(flwer)+1) and int(user_input) != -1):        # might infinite loop
            user_input = input("Invalid Entry, Please enter again: ")
                                      
        if int(user_input) == -1:
            print("\nyou would be returning back to main menu\n")
             
        else:
            info = select(int(followers[int(user_input)-1]))
            user_info(info, int(usr))
    return
################choice 5,6#################


##################choice 4#################
def search(keyword):
    """
    This function finds and resturns the results of a search for a specific keyword
    It first gathers the users whose names match the keyword and then all users whose cities match the keyword
    Returns: list of users based on the keyword (first all users whose name matches in order of increasing name length, and then all users whose city matches in order of increasing name length)
    """
    global connection, cursor
    result = []
    query = 'select name, usr from users where name like "%' + keyword + '%" order by length(name)'
    cursor.execute(query)
    for name in cursor.fetchall():
        result.append(name)
    query = 'select name, usr from users where not name like "%' + keyword + '%" and city like "%' + keyword + '%" order by length(name)'
    cursor.execute(query)
    for name in cursor.fetchall():
        result.append(name)
    return result
    
def select(uid):
    """
    This function finds and returns the necessary information on a specific user
    It uses the given uid to query the database for different information on the user
    Returns: list of information on the user (uid, name, number of tweets, number of users following, number of followers, tweets in order of date with most recent first)
    """
    global connection, cursor
    result = []
    query = 'select usr, name from users where usr = ' + str(uid)
    cursor.execute(query)
    result.append(cursor.fetchall()[0])
    query = 'select count(*) from tweets where writer = ' + str(uid)
    cursor.execute(query)
    result.append(cursor.fetchall()[0][0])
    query = 'select text from tweets where writer = ' + str(uid) + ' order by tdate desc'
    cursor.execute(query)
    result.append(cursor.fetchall())
    query = 'select count(*) from follows where flwer = ' + str(uid)
    cursor.execute(query)
    result.append(cursor.fetchall()[0][0])
    query = 'select count(*) from follows where flwee = ' + str(uid)
    cursor.execute(query)
    result.append(cursor.fetchall()[0][0])
    return result

def follow(uid1, uid2):
    """
    This function checks if uid1 is following uid2, and if not, inserts a new row into the follows table of the database
    It inserts a row specifying that uid1 is following uid2 starting now
    uid1 should be current user
    Returns: N/A
    """
    global connection, cursor
    query = 'select * from follows where flwer = ' + str(uid1) + ' and flwee = ' + str(uid2)
    cursor.execute(query)
    result = cursor.fetchall()
    if len(result) != 0:
        print(f"You are already following {uid2}")
    else:
        query = 'insert into follows values (' + str(uid1) + ', ' + str(uid2) + ', date("now"))'
        cursor.execute(query)
        connection.commit()       
        print(f"You have started following {uid2}")

def user_info(info, current_user):
    print(f"UID: {info[0][0]}   Name: {info[0][1]} \nTweets: {info[1]}   Following: {info[3]}   Followers: {info[4]}")
    print(f"Three most recent tweets:")
    tweet_index = 3
    for i in range(3):
        try:
            print(f"{i+1}. {info[2][i][0]}")
        except:
            print("***No more tweets***")
            break
    selecting2 = True
    while selecting2:
        print("")
        print(f"1. Follow {info[0][0]}\n2. See more tweets\n3. Exit user selection\n")
        response2 = input("Enter your choice: ")
        print("")
        if response2 == "1":
            follow(current_user, info[0][0])
        elif response2 == "2":
            for i in range(tweet_index, tweet_index + 3):
                try:
                    print(f"{i+1}. {info[2][i][0]}")
                except:
                    print("***No more tweets***")
                    break
            tweet_index += 3
        elif response2 == "3":
            selecting2 = False
        else:
            print("Invalid input")    
        
def choice4(current_user):
    """
    This function carries out all of the tasks necessary for the search for users functionality
    Takes user input, and depending on that input directs the user to the correct page/menu while searching for a user
    Offers four choices after initial search, to see more results, select a user, go to previous result page, or exit the search
    Responds accordingly to user input and gives instructions to the user for further actions
    Returns: N/A
    """
    keyword = input("Enter a keyword to search for a user: ")
    result = search(keyword)
    page_index = 1
    user_index = 1
    page_num = math.ceil(len(result) / 5)
    end = False
    if page_num == 0:
        page_index = 0
    print(f"\nPage {page_index} of {page_num}")
    for i in range(5):
        try:
            if len(result[i]) != 0:
                print(f"{i+1}. {result[i][0]}")
        except:
            print("***End of results***")
            end = True
            break
    selecting = True
    while selecting:
        print("")
        print("1. See more results\n2. Select a user\n3. Go to previous result page\n4. Exit user search\n")
        response = input("Enter your choice: ")
        print("")
        if response == "1":
            if page_index >= 0:
                if not end:
                    print(f"Page {page_index + 1} of {page_num}")
                    for i in range(5 * page_index, 5 * (page_index + 1)):
                        try:
                            print(f"{i+1}. {result[i][0]}")
                        except:
                            print("***End of results***")
                            end = True
                            break
                else:
                    print("***No more results available***")
            else:
                print("***No previous pages***")
            page_index += 1
            user_index += 5
            if page_index == page_num:
                end = True
        elif response == "2":
            valid = False
            exited = False
            while not valid:
                try:
                    selection = int(input("Enter the number of the user you would like to select or any non-number character to exit: "))
                    print("")
                    if selection not in range(user_index, user_index + 5) or selection > len(result):
                            print("Invalid input; please select a user from the current page\n")
                    else:
                        info = select(result[selection - 1][1])
                        valid = True
                except:
                    exited = True
                    break
            if not exited:
                user_info(info, current_user[0])
        elif response == "3":
            if page_index > 0:
                page_index -= 1
                user_index -= 5
            if page_index <= page_num:
                end = False                
            if page_index <= 0:
                print("***No previous pages***")
            else:
                if not end:
                    print(f"Page {page_index} of {page_num}")
                    for i in range(5 * (page_index - 1), 5 * page_index):
                        try:
                            print(f"{i+1}. {result[i][0]}")
                        except:
                            print("***End of results***")
                            end = True
                            break
                else:
                    print("***No more results available***") 
        elif response == "4":
            selecting = False            
        else:
            print("Invalid input")
############choices 4#############


###########choice 3#############

def find_tweets(*keywords):
    global offset
    placeholders_tweets = ' OR '.join(['tweets.text LIKE ?' for _ in range(len(keywords))])
    placeholders_mentions = ' OR '.join(['mentions.term LIKE ?' for _ in range(len(keywords))])

    query = f'''
        SELECT tweets.* FROM tweets
        LEFT JOIN mentions ON tweets.tid = mentions.tid
        WHERE ({placeholders_tweets}) OR ({placeholders_mentions})
        ORDER BY tweets.tdate DESC
        LIMIT 5 OFFSET {offset * 5}
    '''

    # Provide values for both sets of placeholders
    values = tuple(['%' + kw + '%' for kw in keywords] * 2)

    cursor.execute(query, values)
    return cursor.fetchall()

def more_tweets():
    global more
    global offset
    global matches
    
    while more.lower() == 'y':
        matches = find_tweets(*keywords)

        if matches:
            if len(matches)==5 or len(matches)==1:
                for tweet in matches:
                    print(tweet)
            else:
                for tweet in matches[:-1]:
                    print(tweet)
            offset += 1
            more = input("See more tweets? y/n:").lower()
        else:
            print("No more matching tweets.")
            more = 'n'  # Break the loop if there are no more matches

def select_tweet():
    isint = False
    while not isint:
        try:
            selected_TID = int(input("Enter TID: "))
            isint = True
        except:
            print("Invalid input")

    select_query = f'''
        SELECT t.tid, t.writer, t.tdate, t.text,
        COUNT(DISTINCT r.usr) AS Retweets_Count,
        COUNT(DISTINCT r2.tid) AS Replies_Count
        FROM tweets t
        LEFT JOIN retweets r ON t.tid = r.tid
        LEFT JOIN tweets r2 ON t.tid = r2.replyto
        WHERE t.tid = {selected_TID}
        GROUP BY t.tid, t.writer, t.tdate, t.text;
        '''
    cursor.execute(select_query)
    result = cursor.fetchone()

    if result:
        print(f'Tweet: {result[0]}, {result[1]}, {result[2]}, {result[3]}')
        print(f'Retweets: {result[4]}')
        print(f'Replies: {result[5]}')
    else:
        print("No tweet found for the given TID.")

def retweet(usr, tid):
    # Check if the tweet exists
    tweet_exists_query = f'SELECT 1 FROM tweets WHERE tid = ? LIMIT 1;'
    cursor.execute(tweet_exists_query, (tid,))
    tweet_exists = cursor.fetchone()

    if tweet_exists and tweet_exists[0] == 1:
        # Tweet exists, proceed with the retweet
        retweet_date = time.strftime("%Y-%m-%d")
        tweet_exists_q = f'SELECT * FROM retweets WHERE usr = ? AND tid = ?;'
        cursor.execute(tweet_exists_q, (usr, tid))
        tweet_exists_1 = cursor.fetchone()
        if tweet_exists_1 == None:
            insert_query = '''
                INSERT INTO retweets (usr, tid, rdate)
                VALUES (?, ?, ?);
            '''
            cursor.execute(insert_query, (usr, tid, retweet_date))
            connection.commit()
            print("Retweet successfully added.")
        else:
            print("You have already retweeted this tweet.")
    else:
        # Tweet doesn't exist
        print("The specified tweet does not exist.")



def menu_options(current_user):
    global more, keywords, offset
    offset = 0
    user_choice = 0
    while user_choice != 6:
        if user_choice == 1:
            more = 'y'
        elif user_choice == 2:
            select_tweet()
        elif user_choice == 3:
            offset = 0
            input_keywords = input("Keywords to search:")
            keywords = input_keywords.split(', ')
            more = 'y'  # Set more to 'y' when searching different keywords
        elif user_choice == 4:
            isint = False
            while not isint:
                try:
                    tweet_id = int(input("Enter TID to retweet: "))
                    isint = True
                except:
                    print("Invalid input")
            retweet(current_user[0],tweet_id)
        elif user_choice == 5:
            isint = False
            while not isint:
                try:
                    replyTo = int(input("Enter TID to reply to: "))
                    isint = True
                except:
                    print("Invalid input")
            tweet_exists_query = f'SELECT 1 FROM tweets WHERE tid = ? LIMIT 1;'
            cursor.execute(tweet_exists_query, (replyTo,))
            tweet_exists = cursor.fetchone()

            if tweet_exists and tweet_exists[0] == 1:
                # Tweet exists, proceed with the retweet
                current_usr = int(current_user[0])
                tweet_text = input("Enter Reply: ")
                compose_tweet(current_usr, tweet_text, replyTo)
            else:
                # Tweet doesn't exist
                print("The specified tweet does not exist.")

        more_tweets()  # Call more_tweets once after processing user's choice
        isint = False
        while not isint:
            try:
                user_choice = int(input("Make a selection:\n1. See More Tweets\n2. Select a Tweet\n3. Search different Keyword\n4. Retweet a Tweet\n5. Reply to a tweet\n6. Return to Home Screen\n"))
                isint = True
            except:
                print("Invalid input")
##########choice 3##############


def list_all(current_user):
    '''
    This function is used to display all tweets or retweets from users
    who are being followed; It has options to search for tweets, search for users,
    compose a tweet, list followers and logout
    '''
    global connection, cursor, keywords, offset, more
    print("\n Hello ", current_user[2], "! \n")
    print("1. List all tweets")
    print("2. List all retweets")
    print("3. Search for tweets")
    print("4. Search for users")
    print("5. Compose a tweet")
    print("6. List followers")
    print("7. Logout and Back to main menu")
    choice = input("\n Enter your choice: ")
    if choice == "1":
        cursor.execute("select flwee from follows where flwer = ?", (current_user[0],))
        result = cursor.fetchall()
        if len(result) == 0:
            print("\n No tweets to display, you did't follow anybody yet\n")
            list_all(current_user)
        else:
            tweet_list = []
            for i in range(len(result)):
                cursor.execute("select tid, writer, tdate, text, replyto from tweets where writer = ? order by tdate desc", (result[i][0],))
                result1 = cursor.fetchall()
                for j in range(len(result1)):
                    tweet_list.append(result1[j])
            if len(tweet_list) == 0:
                print("\n No tweets to display\n")
                list_all(current_user)
            tweet_list.sort(key=lambda x: x[2], reverse=True)
            pages = 1
            current_page = 1
            next_page = False
            last_page = False
            if len(tweet_list) > 5 and len(tweet_list) % 5 != 0:
                pages = len(tweet_list) // 5 + 1
                next_page = True
            if pages == current_page:
                last_page = True
            
            while next_page and not last_page:
                current_page = current_page
                print("Page ", current_page, " of ", pages)
                for j in range((current_page-1)*5, (current_page-1)*5+5):
                        print_tweet(tweet_list, j)
                next_page_ordetails_input = input("Next page? (y/n) or \nsee tweet details? (t) or \nreply to a tweet? (r): ")
                if next_page_ordetails_input == "y" or next_page_ordetails_input == "Y":
                        current_page += 1
                        if current_page == pages:
                            next_page = False
                            last_page = True
                # user select a tweet to see the number of retweets and replies
                elif next_page_ordetails_input == "t" or next_page_ordetails_input == "T":
                    print_tweet_details()
                elif next_page_ordetails_input == "r" or next_page_ordetails_input == "R":
                    replyTo = int(input("Enter TID to reply to: "))
                    cursor.execute("select tid from tweets where tid = ?", (replyTo,))
                    result = cursor.fetchone()
                    while result == None:
                        print("Invalid TID")
                        replyTo = int(input("Enter TID to reply to: "))
                        cursor.execute("select tid from tweets where tid = ?", (replyTo,))
                        result = cursor.fetchone()
                    tweet_text = input("Enter Reply: ")
                    current_usr = int(current_user[0])
                    compose_tweet(current_usr, tweet_text, replyTo)
                else:
                    break
            if last_page and not next_page:
                print("Page ", current_page, " of ", pages)
                for j in range((current_page-1)*5, (current_page-1)*5 + len(tweet_list)%5):
                    print_tweet(tweet_list, j)
                details_input = input("see tweet details? (t) or \nreply to a tweet? (r): ")
                if details_input == "t" or details_input == "T":
                    print_tweet_details()
                elif details_input == "r" or details_input == "R":
                    replyTo = int(input("Enter TID to reply to: "))
                    cursor.execute("select tid from tweets where tid = ?", (replyTo,))
                    result = cursor.fetchone()
                    while result == None:
                        print("Invalid TID")
                        replyTo = int(input("Enter TID to reply to: "))
                        cursor.execute("select tid from tweets where tid = ?", (replyTo,))
                        result = cursor.fetchone()
                    tweet_text = input("Enter Reply: ")
                    current_usr = int(current_user[0])
                    compose_tweet(current_usr, tweet_text, replyTo)
            list_all(current_user)
    elif choice == "2":
        cursor.execute("select flwee from follows where flwer = ?", (current_user[0],))
        result = cursor.fetchall()
        if len(result) == 0:
            print("\n No tweets to display, you did't follow anybody yet\n")
            list_all(current_user)
        else:
            retweet_list = []
            for i in range(len(result)):
                cursor.execute("select r.tid, r.rdate, t.writer, t.tdate, t.text from retweets r left join tweets t ON r.tid = t.tid where usr = ?", (result[i][0],))
                result1 = cursor.fetchall()
                for j in range(len(result1)):
                    retweet_list.append(result1[j])
            retweet_list.sort(key=lambda x: x[3], reverse=True)
            if len(retweet_list) == 0:
                print("\n No retweets to display\n")
                list_all(current_user)
            pages = 1
            current_page = 1
            next_page = False
            last_page = False
            if len(retweet_list) > 5 and len(retweet_list) % 5 != 0:
                pages = len(retweet_list) // 5 + 1
                next_page = True
            if pages == current_page:
                last_page = True
            
            while next_page and not last_page:
                current_page = current_page
                print("Page ", current_page, " of ", pages)
                for j in range((current_page-1)*5, (current_page-1)*5+5):
                    print_retweet(retweet_list, j)
                next_page_or_details_input = input("Next page? (y/n) or \nsee tweet details? (t) or \nreply to a tweet? (r): ")
                if next_page_or_details_input == "y" or next_page_or_details_input == "Y":
                        current_page += 1
                        if current_page == pages:
                            next_page = False
                            last_page = True
                elif next_page_or_details_input == "t" or next_page_or_details_input == "T":
                    print_tweet_details()
                elif next_page_or_details_input == "r" or next_page_or_details_input == "R":
                    replyTo = int(input("Enter TID to reply to: "))
                    cursor.execute("select tid from tweets where tid = ?", (replyTo,))
                    result = cursor.fetchone()
                    while result == None:
                        print("Invalid TID")
                        replyTo = int(input("Enter TID to reply to: "))
                        cursor.execute("select tid from tweets where tid = ?", (replyTo,))
                        result = cursor.fetchone()
                    tweet_text = input("Enter Reply: ")
                    current_usr = int(current_user[0])
                    compose_tweet(current_usr, tweet_text, replyTo)
                else:
                    break
            if last_page and not next_page:
                print("Page ", current_page, " of ", pages)
                for j in range((current_page-1)*5, (current_page-1)*5 + len(retweet_list)%5):
                    print_retweet(retweet_list, j)
                details_input = input("\nsee tweet details? (t) or \nreply to a tweet? (r): ")
                if details_input == "t" or details_input == "T":
                    print_tweet_details()
                elif details_input == "r" or details_input == "R":
                    replyTo = int(input("Enter TID to reply to: "))
                    cursor.execute("select tid from tweets where tid = ?", (replyTo,))
                    result = cursor.fetchone()
                    while result == None:
                        print("Invalid TID")
                        replyTo = int(input("Enter TID to reply to: "))
                        cursor.execute("select tid from tweets where tid = ?", (replyTo,))
                        result = cursor.fetchone()
                    tweet_text = input("Enter Reply: ")
                    current_usr = int(current_user[0])
                    compose_tweet(current_usr, tweet_text, replyTo)
            list_all(current_user)

    elif choice == "3":
        offset = 0
        input_keywords = input("Keywords to search:")
        keywords = input_keywords.split(', ')
        more = 'y'
        menu_options(current_user)
        list_all(current_user)
    elif choice == "4":
        choice4(current_user)
        list_all(current_user)
    elif choice == "5":
        tweet_str = input("Please provide a tweet you would like to compose:\n")
        value = compose_tweet(current_user[0], tweet_str)
        if value == True:
            print("\nTweet is composed successfully\n")
            list_all(current_user)
        else:
            print("\nSign-in failed\n")
            login_reg_screen() 
    elif choice == "6":
        list_followers(current_user[0])
        list_all(current_user)
    elif choice == "7":
        sp.run('clear', shell=True)
        print("\n Goodbye ", current_user[2], "!")
        print("log out successful!\n")
        main()
    else:
        print("Invalid choice")
        list_all(current_user)



def register():
    '''
    This function is used to register the user
    '''
    global connection, cursor
    # generate a random user id
    cursor.execute("select usr from users")
    result = cursor.fetchall()
    user_id = random.randint(1, 1000)
    while user_id in result:
        user_id = random.randint(1, 1000)

    name = input("Name: ")
    email = input("Email: ")
    while "@" not in email:
        print("Invalid email format, should include @")
        email = input("Email: ")
    city = input("City: ")
    valid = False
    while not valid:
        timezone = input("Timezone: ")
        try:
            timezone = int(timezone)
            if timezone not in range(-12, 13):
                print("Invalid timezone, timezone should be an integer between -12 and 12")
            else:
                valid = True
        except:
            print("Invalid timezone, should be int")
    
    password = getpass.getpass("Password: ")
    try:
        cursor.execute("insert into users values (?, ?, ?, ?, ?, ?)", (user_id, password, name, email, city, timezone))
        connection.commit()
        print("Registration Successful", "your user id is: ", user_id)
        return ("Registration Successful", (user_id, password, name, email, city, timezone))
    except sqlite3.Error as e:
        print(e)


def connect_db():
    '''
    This function is used to create the tables in the database. It is called in main.py
    '''
    global connection, cursor
    db_input = input("Enter database name: ")
    path = "./" + db_input
    if os.path.isfile(path):
        connect(path)
    else:
        print("Database does not exist\n")
        connect_db()



def main():
    '''
    main function for creating database and calling login_reg_screen function
    '''
    global run

    if run == 1:
        connect_db()
        run = 0
        
    login_status = login_reg_screen()
  
    if login_status[0] == "Successful":
        current_user = login_status[1]
        list_all(current_user)
    if login_status[0] == "Registration Successful":
        login_status = login_reg_screen()
        if login_status[0] == "Successful":
            current_user = login_status[1]
            list_all(current_user)

if __name__ == "__main__":
    main()
