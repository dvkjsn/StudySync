before you start working, do the following in your terminal:

1. python3 -m venv venv
2. source venv/bin/activate (THIS IS FOR MAC, look up how to activate venv for others)
3. pip install -r requirements.txt
4. python app.py
after running python app.py, you'll see a server link that you can open in your web browser

if you just cloned the repo for the first time, run this command in terminal so that db is initialized:
python init_db.py

then, you should see studysync.db file in your vscode and you can mess with the website...
this means that any changes made to the db when you edit stuff on the website will not show up on others' dbs, unless you push the db file... but i think that may cause merge conflicts so don't push the studysync.db file unless you tell everyone beforehand