import hashlib
import os
import pdb
import shutil
import sqlite3
import sys
import unicodedata
import urllib
from urllib import request

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

def md5File(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def downloadEntity(src):
    directory = './static/'
    filename, extension = os.path.splitext(src)

    local_filename, headers = urllib.request.urlretrieve(src)
    hashed_filename = md5File(local_filename)
    to_file = directory + hashed_filename + extension
    
    shutil.move(local_filename, to_file)
    print('moved ' + colorize(local_filename, 1) + ' to ' + colorize(to_file, 2))

    return to_file

def downloadEntities():
    conn = sqliteConnect()

    statement = "select media_url,id,media_preview from tw_entities where local_hash is null;"
    entitiesToDownload = sqliteStatement(conn, statement, ())

    if not entitiesToDownload:
        print('-')
        return

    for n in entitiesToDownload:
        src = n[0]
        entity_id = n[1]
        try:
            local_file = downloadEntity(src)
            
            '''
            INSERT INTO memos(id,text) 
            SELECT 5, 'text to insert' 
            WHERE NOT EXISTS(SELECT 1 FROM memos WHERE id = 5 AND text = 'text to insert');
            '''

            statement = "UPDATE tw_entities SET local_hash = '{0}' WHERE id = {1} AND NOT EXISTS(SELECT 1 FROM tw_entities WHERE local_hash = '{0}');".format(local_file[8:], entity_id)
            sqliteStatement(conn, statement, ())
            print(colorize(statement, 2))

        except Exception as e:
            print('ERROR fetching : ' + src + ": " + str(e))

    conn.commit()

downloadEntities()
