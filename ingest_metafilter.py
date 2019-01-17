import base64
from bs4 import BeautifulSoup
from collections import OrderedDict
import datetime
import pdb
import pprint
import re
import requests
import simplejson
import sqlite3
import sys
import time
import yaml

with open("secrets.yaml", 'r') as stream:
    try:
        secrets = yaml.load(stream)
    except yaml.YAMLError as exc:
        print(exc)
        sys.exit()

pp = pprint.PrettyPrinter(indent=4)

def sqliteConnect():
    db_file = "twitter.db"

    try:
        conn = sqlite3.connect(db_file)
        conn.text_factory = lambda x: unicode(x, 'utf-8', 'ignore')
        return conn
    except Exception as e:
        print('sqliteConnect ERROR: ' + str(e) + ' for db_file: ' + db_file)
        pdb.set_trace()
        sys.exit()

def sqliteStatement(conn, statement, variables=None):
    try:
        c = conn.cursor()
        if variables:
	        c.execute(statement, variables)
        else:
            c.execute(statement)
        conn.commit()
        #c.close()

        return c.fetchall()
    except Exception as e:
        print('sqliteStatement ERROR: ' + str(e) + " for statement: \n\n" + statement + "\n\n& variables\n\n" +variables)
        sys.exit()

def callFavePosts(uid, favType='comments', page=0):
    '''
        http://www.metafilter.com/favorites/1/comments/4/
    '''

    baseUrl = 'http://www.metafilter.com/favorites/'
    if page == 0:
        url = baseUrl + '/' + str(uid) + '/' + favType + '/'
    else:
        url = baseUrl + '/' + str(uid) + '/' + favType + '/' + str(page) + '/'
    return curl(url)

def curl(url):
    headers = {
        'User-Agent': 'conical v0.0.1',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'Accept-Encoding': 'gzip'
    }
    req = requests.Request('GET', url, headers=headers)
    prepped = req.prepare()

    s = requests.Session()
    resp = s.send(prepped)
    return resp.content

#Go through the favorites pages, and save all of your favorites comments' comment IDs, as well as the post IDs they came from.
def parseFavePage(conn, resp, fave_tuples):
    soup = BeautifulSoup(resp, 'html.parser')
    
    favesCountText = soup.find(class_='smallcopy chromeleft')
    #print(favesCountText.text)

    favesCountMatches = re.search('Displaying comments ([0-9]+) to ([0-9]+) of ([0-9]+)', favesCountText.text)
    if not favesCountMatches:
        return None, None
    maxFaveOnPage = int(favesCountMatches.group(2))
    maxFaves = int(favesCountMatches.group(3))

    print('Progress: ' + str(maxFaveOnPage) + ' / ' + str(maxFaves))

    bComplete = False
    if maxFaveOnPage >= maxFaves:
        bComplete = True

    faveComments = {}

    faves = soup.find_all(href=re.compile("www\.metafilter\.com\/.*\/.*#.*"))
    for f in faves:
        if type(f).__name__ is not 'Tag':
            continue
        if f.text == 'more' or f.text == '>':
            continue
        #@TODO: don't hardcode the subdomain, as this currently only gets the blue
        faveUrl = re.search('http://www.metafilter.com/([0-9]+)/(.*)#(.*)$', f['href'])
        if not faveUrl:
            continue
        commentId = int(faveUrl.group(3))
        postId = str(faveUrl.group(1))# + '/' + faveUrl.group(2)
        
        '''addMediaStatement = "INSERT OR IGNORE INTO mefi_comments (post_id, comment_id) VALUES (?, ?)"
        addMediaVariables = (postId, int(commentId))
        print(addMediaStatement, addMediaVariables)
        sqliteStatement(conn, addMediaStatement, addMediaVariables)

        addMediaStatement = "INSERT OR IGNORE INTO mefi_posts (post_id) VALUES (?)"
        addMediaVariables = (postId)
        print(addMediaStatement, addMediaVariables)
        sqliteStatement(conn, addMediaStatement, addMediaVariables)'''
        if postId in fave_tuples:
            fave_tuples[postId].append(commentId)
        else:
            fave_tuples[postId] = [commentId]

    return bComplete

def ingestCommentFavesLoop(conn, page, fave_tuples):
    resp = callFavePosts(secrets['mefiUid'], 'comments', page)
    if not resp:
        print("no resp? " + type(resp).__name__)
        sys.exit()

    return parseFavePage(conn, resp, fave_tuples)

def populateCommentFaveDataLoop(conn, i, fave_tuples):
    queryList = {}

    for post_id in fave_tuples: #iterate through the list of posts. Posts can have multiple children, each of which is a favorited comment.
        for comment_id in post_id:
            statement = "SELECT * FROM mefi_comments WHERE comment_text IS NULL AND comment_id = ?"
            variables = (comment_id)
            existing_comment = sqliteStatement(conn, statement, variables)
            if existing_comment:
                fave_tuples[post_id].remove(comment_id) #this comment already exists in the db, so remove it from the set of 

        if len(fave_tuples[post_id]) == 0:
            del(fave_tuples[post_id]) #if there are no comments you need to grab, then remove the post entirely.

    count = 0
	#http://www.metafilter.com/169767/My-family-and-I-cant-live-in-good-intentions-Marge#7188409
    for postId in fave_tuples:
        count += 1
        print('populateCommentFaveDataLoop count: '+ str(count))
        if count < 100:
            continue

        comments = fave_tuples[postId]
        #curl the post and get its HTML contents
        #@TODO: don't hardcode the subdomain, as this currently only gets the blue
        url = 'http://www.metafilter.com/{0}'.format(postId)
        postHtml = curl(url)

        statement = "SELECT full_html FROM mefi_posts WHERE post_id = ?"
        #if the post already exists in the db, skip it. This doesn't take HTML deltas into consideration, which it should.
        post_exists = sqliteStatement(conn, statement, (postId,))
        if post_exists:
            progress_msg('skipping post #{0}, since it already exists'.format(postId))
        else:
            progress_msg('Inserting post #{0}'.format(postId))
            #now go find the text of all of the comments favorited in that post, and dump them in the db.
            parseAndSavePost(conn, postId, postHtml)
     
	parseAndSaveComments(conn, postId, postHtml, comments)

    return True

	
def parseAndSavePost(conn, postId, postHtml):
    soup = BeautifulSoup(postHtml, 'html.parser')
  
    aboveTheFold = soup.find(class_='copy')
    postByline = aboveTheFold.find(class_='postbyline')
    if postByline:
        byline = postByline.extract()
    else:
        byline = soup.find(class_='postbyline')
    post_author_metadata = byline.find('a')

    postAuthor = post_author_metadata.text

    #postText = aboveTheFold.encode('ascii', 'ignore')
    postText = str(aboveTheFold)
   
    postHeader = soup.find(class_='posttitle')
    smallCopy = postHeader.find(class_='smallcopy')
    postMetadata = smallCopy.extract()
    postTitle = postHeader.text.strip('\n')
    subscribe = postMetadata.find('a')
    subscribe.extract()
    subscribe = postMetadata.find('a')
    subscribe.extract()
    postTimestamp = postMetadata.text
    postTimestamp = postTimestamp.encode("ascii", 'ignore').strip()

    #@TODO: parse the post data and insert it into mefi_posts as appropriate.
    progress_msg('Inserting post #{0}'.format(postId))
    statement = "INSERT OR IGNORE INTO mefi_posts (post_id, post_title, post_author, post_text, full_html) VALUES (?, ?, ?, ?, ?)"
    variables = (postId, postTitle, postAuthor, postText, str(postHtml))
    #print(statement, variables)
    sqliteStatement(conn, statement, variables)


def progress_msg(msg):
    print(msg)

def is_number(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


def parseAndSaveComments(conn, postId, postHtml, comments):
    soup = BeautifulSoup(postHtml, 'html.parser')

    commentTrees = soup.find_all(class_='comments')

    #'2' appears to be prepended to at least some mefi comment faves, by comment id. Metatalk might be 6?
    #Might be subsite designation or something.

    #iterate through all comments in the thread
    i = 0
    for commentTree in commentTrees:
        hrefs = commentTree.find_all('a')
        #iterate through all links in the comment
        for href in hrefs:
            #if we find a favorite anchor that matches any of the favorites we're looking for...
            for comment in comments:
                if not href.get('href'):
                    continue
                if str(comment) in href['href']:
                    '''
			(Pdb) a_s[0].__str__
			<bound method Tag.__str__ of <a href="https://www.metafilter.com/user/36311" target="_self">T.D. Strange</a>>
			(Pdb) a_s[1].__str__
			<bound method Tag.__str__ of <a href="/170414/Bastards-stole-their-power-from-the-victims-of-the-Us-v-Them-years#7223687" target="_self">7:19 PM</a>>
			(Pdb) a_s[2].__str__
			<bound method Tag.__str__ of <a href="/favorited/2/7223687" style="font-weight:normal;" title="81 users marked this as favorite">81 favorites</a>>
                    '''
                    try:
                        user = hrefs[0]
                        link = hrefs[1]
                        faves_data = hrefs[2]
                    except Exception as e:
                        origCommentTree = commentTree
                        commentTree = commentTrees[i]
                        
                        hrefs = commentTree.find_all('a')
                        user = hrefs[0]
                        link = hrefs[1]
                        faves_data = hrefs[2]
 
                        pdb.set_trace()

                    #u'posted by orange swan at 8:39 AM  on November 8, 2017 [79 favorites] '
                    date_start = commentTree.text.rfind(' at ')
                    date_end = commentTree.text.rfind('[')
                    date_str = commentTree.text[date_start:date_end].strip()
                  
                    if not is_number(date_str[-4:]): #No year provided, meaning it's this year. add that manually
                        date_str += ' ' + str(time.localtime().tm_year)
                    date_str.strip()               
 
                    try:
                        unixTime = datetime.datetime.strptime(date_str, 'at %I:%M %p  on %B %d %Y').strftime('%s')
                    except:
                        unixTime = datetime.datetime.strptime(date_str, 'at %I:%M %p  on %B %d, %Y').strftime('%s')
                    unixTime = int(unixTime)

                    commentText = commentTree.get_text()
                    
                    comment = int(str(comment)[1:])
                    addMediaStatement = "UPDATE mefi_comments SET comment_text = ? where comment_id = ?"
                    #addMediaStatement = "UPDATE mefi_comments SET comment_text=?, comment_author=?, comment_text=?, comment_timestamp=? where comment_id = ?"
                    addMediaVariables = (commentText, comment)
                    #sqliteStatement(conn, addMediaStatement, addMediaVariables)

                    addFavoritesStatement = "INSERT OR IGNORE INTO favorites (owner, added, contextual_id, favorite_type) VALUES (?, ?, ?, ?)"
                    addFavoritesVariables = (1, int(time.time()), comment, 2)
                    #sqliteStatement(conn, addFavoritesStatement, addFavoritesVariables)
    i += 1


i = 0
fave_tuples = {}
conn = sqliteConnect()
while True:

    if ingestCommentFavesLoop(conn, i, fave_tuples):
        break
    i = i + 1

'''We've ingested all of the post/comment ids for favorite comments. Now let's do a second pass over
those rows and grab the supporting details'''
i = 0
print('Kicking off')
while True:
#while i == 0:
    print('Progress: Page #' + str(i))
    if populateCommentFaveDataLoop(conn, i, fave_tuples):
        break
    i = i + 1
