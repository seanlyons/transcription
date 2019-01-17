import datetime
from flask import Flask
import pdb
from flask import render_template
from flask import request
from flask import send_from_directory
import re
from hashlib import sha512
import simplejson
import sqlite3
import sys

app = Flask(__name__)

def colorize(string, n):
    attr = []
    if n % 2 == 0:
        # green
        attr.append('32')
    else:
        # red
        attr.append('31')
    return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), string)

def sqliteConnect():
    db_file = "twitter.db"

    try:
        return sqlite3.connect(db_file)
    except Exception as e:
        print('sqliteConnect ERROR: ' + str(e) + ' for db_file: ' + colorize(db_file, 1))
        sys.exit()

def sqliteStatement(conn, statement, variables):
    try:
        c = conn.cursor()
        c.execute(statement, variables)

        return c.fetchall()
    except Exception as e:
        print('sqliteStatement ERROR: ' + str(e) + " for statement: \n\n" + colorize(statement, 1))
        sys.exit()

def listUsers():
    conn = sqliteConnect()
    statement = "select id from users"
    users = sqliteStatement(conn, statement, ())
    userList = []
    for user in users:
        userList.append(user[0])
    return userList

def showUserFavorites(user_id):
    i = 0
    favorite_tweets = []

    conn = sqliteConnect()
    statement = "select tw_created_at, tw_full_text, tw_user, tw_id from tw_tweets order by tw_id"
    tweetData = sqliteStatement(conn, statement, ())
    

    for tweet in tweetData:
        tw_user_id = tweet[2]
        statement = "select tw_screen_name, tw_description, tw_name, tw_profile_image_url from tw_users where tw_id = {0}".format(tw_user_id)
        userData = sqliteStatement(conn, statement, ())[0]
    
        i += 1
        #if i >= 5:
            #break
        #print('i = ' + str(i))

        currentTime = datetime.datetime.fromtimestamp(tweet[0]).strftime('%I:%M %p - %d %b %Y')
        #pdb.set_trace()
        nonce = (str(user_id) + '_' + str(tweet[3]) + '_' + currentTime).encode('utf-8')
        nonce = sha512(nonce).hexdigest()
        atom = {
            'id': tweet[3],
            'fave_id': i,
            #5:16 PM - 31 Oct 2013
            'created_at': datetime.datetime.fromtimestamp(tweet[0]).strftime('%I:%M %p - %d %b %Y'),
            'full_text': re.sub('https?:\/\/t\.co\/[a-zA-Z0-9]+', '', tweet[1].replace('\n', '<br/>')),
            'nonce': nonce,
            'author': {
                'screen_name': userData[0],
                'description': userData[1],
                'name': userData[2],
                'profile_image_url': userData[3]
            }
        }
    
        statement = "select media_type, media_preview, media_url, local_hash from tw_entities where tweet_id = {0}".format(tweet[3])
        entitiesData = sqliteStatement(conn, statement, ())
        print(simplejson.dumps(entitiesData))
        print('---')
        if entitiesData and len(entitiesData) >= 1:
            atom['entities'] = []
            for entityData in entitiesData:
                if len(entityData) < 3:
                    pdb.set_trace()
                if not entityData[0] or not entityData[3]:
                    continue
                try:
                    atom['entities'].append({
                        'media_type': entityData[0],
                        'media_url': 'static' + entityData[3],
                        'media_preview':  entityData[1]
                    })
                except:
                    pdb.set_trace()
        favorite_tweets.append(atom)

    #pdb.set_trace()
    #print('skipped ' + str(skipped))
    return favorite_tweets

'''
		CREATE TABLE mefi_comments (
			id integer PRIMARY KEY,
			post_id text,
			comment_id UNSIGNED BIG INT,
			comment_author text,
			comment_text text,
			comment_timestamp integer,
			UNIQUE(comment_id)
		);
'''


def _showUserFavorites_(user_id):
    conn = sqliteConnect()
    statement = "select added,contextual_id from favorites where owner = {0} and favorite_type = {1} order by contextual_id".format(user_id, 1)
    favorites_ids = sqliteStatement(conn, statement, ())
    favorite_tweets = []
    skipped = 0
    i = 1
    for favorite_id in favorites_ids:
        #if favorite_id[1] != 911633126396514304 and favorite_id[1] != 918188230524243968:
        #    skipped += 1
        #    continue
        pdb.set_trace()
        statement = "select tw_created_at, tw_full_text, tw_user from tw_tweets where tw_id = {0}".format(favorite_id[1])
        tweetData = sqliteStatement(conn, statement, ())[0]

        tw_user_id = tweetData[2]
        statement = "select tw_screen_name, tw_description, tw_name, tw_profile_image_url from tw_users where tw_id = {0}".format(tw_user_id)
        userData = sqliteStatement(conn, statement, ())[0]

        i += 1
        if i >= 5:
            return favorite_tweets 

        tweet = {
            'id': favorite_id[1],
            'fave_id': i,
            #5:16 PM - 31 Oct 2013
            'created_at': datetime.datetime.fromtimestamp(tweetData[0]).strftime('%I:%M %p - %d %b %Y'),
            'full_text': tweetData[1].replace('\n', '<br/>'),
            'author': {
                'screen_name': userData[0],
                'description': userData[1],
                'name': userData[2],
                'profile_image_url': userData[3]
            }
        }

        statement = "select media_type, media_preview, media_url, local_hash from tw_entities where tweet_id = {0}".format(favorite_id[1])
        entitiesData = sqliteStatement(conn, statement, ())
        print(simplejson.dumps(entitiesData))
        print('---')
        if entitiesData and len(entitiesData) >= 1:
            tweet['entities'] = []
            for entityData in entitiesData:
                if len(entityData) < 3:
                    pdb.set_trace()
                if not entityData[0] or not entityData[3]:
                    continue
                try:
                    tweet['entities'].append({
                        'media_type': entityData[0],
                        'media_url': 'static' + entityData[3],
                        'media_preview':  entityData[1]
                    })
                except:
                    pdb.set_trace()
        
        favorite_tweets.append(tweet)

    print('skipped ' + str(skipped))
    return favorite_tweets

'''
		CREATE TABLE mefi_comments (
			id integer PRIMARY KEY,
			post_id text,
			comment_id UNSIGNED BIG INT,
			comment_author text,
			comment_text text,
			comment_timestamp integer,
			UNIQUE(comment_id)
		);
'''

def showMefiFavorites(user_id):
    return None
    conn = sqliteConnect()
    statement = "select added,contextual_id from favorites where owner = {0} and favorite_type = {1}".format(user_id, 2)
    favorites_ids = sqliteStatement(conn, statement, ())
    favorite_comments = []
    skipped = 0
    for favorite_id in favorites_ids:
        #if favorite_id[1] != 911633126396514304 and favorite_id[1] != 918188230524243968:
        #    skipped += 1
        #    continue
        #statement = "select tw_created_at, tw_full_text, tw_user from tw_tweets where tw_id = {0}".format(favorite_id[1])
        statement = "select comment_timestamp, comment_text, comment_author from mefi_comments where comment_id = {0}".format(favorite_id[1])
        tweetData = sqliteStatement(conn, statement, ())[0]

        pdb.set_trace()

        tw_user_id = tweetData[2]
        statement = "select id, tw_screen_name, tw_description, tw_name, tw_profile_image_url from tw_users where tw_id = {0}".format(tw_user_id)
        userData = sqliteStatement(conn, statement, ())[0]

        tweet = {
            'id': favorite_id[1],
            #5:16 PM - 31 Oct 2013
            'created_at': datetime.datetime.fromtimestamp(tweetData[0]).strftime('%I:%M %p - %d %b %Y'),
            'full_text': tweetData[1].replace('\n', '<br/>'),
            'author': {
                'screen_name': userData[0],
                'description': userData[1],
                'name': userData[2],
                'profile_image_url': userData[3]
            }
        }

        statement = "select media_type, media_preview, media_url, local_hash from tw_entities where tweet_id = {0}".format(favorite_id[1])
        entitiesData = sqliteStatement(conn, statement, ())
        print(simplejson.dumps(entitiesData))
        print('---')
        if entitiesData and len(entitiesData) >= 1:
            tweet['entities'] = []
            for entityData in entitiesData:
                if len(entityData) < 3:
                    pdb.set_trace()
                if not entityData[0] or not entityData[3]:
                    continue
                try:
                    tweet['entities'].append({
                        'media_type': entityData[0],
                        'media_url': 'static' + entityData[3],
                        'media_preview':  entityData[1]
                    })
                except:
                    pdb.set_trace()
        
        favorite_tweets.append(tweet)

    print('skipped ' + str(skipped))
    return favorite_tweets
        
    
############################# FLASK ROUTING #############################

@app.route('/')
def list_users():
    userList = listUsers()
    return render_template('listUsers.html', userList=userList)

@app.route('/<int:user_id>')
def show_favorites(user_id):
    favoriteTweets = showUserFavorites(user_id)
    #favoriteMefiComments = showMefiFavorites(user_id)
	
    return render_template('showUserFavorites.html', favorites=favoriteTweets)

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/tag', methods=['POST'])
def post_request():
	#pdb.set_trace()
    #return render_template('showUserFavorites.html', favorites=favoriteTweets)
    return 'zzz'


