1. install sqlite: `sudo apt-get install sqlite3`
2. create a `twitter` db in sqlite: `python3.6 create_sqlite.py`
3. write a 3-line `secrets.yaml`:
```d
consumerKey: DEAD...B33F
consumerSecret: B00F...F00
userName: 
```
for the values documented at https://developer.twitter.com/en/docs/basics/authentication/overview/application-only. the userName variable is the account that you want to scrape favorites from.

4. make sure you have pip (https://pip.pypa.io/en/stable/installing/)
pip install dependencies: `sqlite3`, `flask`, `simplejson`, `PyYAML`, `requests`, `urllib`. Your system probably already has most/all of these; bash on win10 doesn't appear to, for some reason.
5. make a `static` dir to deposit downloaded assets into: `mkdir static`.
6. download all of your favorites: `python3.6 ingest_twitter.py`
7. download all of the media embedded in those favorites: `python3.6 ingest_entities.py`
8. set up the frontend python script as a flask app: `dd`
9. create a user in the db: `sqlite3 twitter.db`; `insert into users values (1, 'my_email_address@example.com', 'foo', 'plainttext');`;
10. start up flask: `python3 -m flask run`
11. go to your site, listing users: `http://localhost:5000/`
12. click `1` and view all favorites.

	
