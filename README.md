
=====ENVIRONMENT SETUP=====

# create your own venv using
python3 -m venv venv

# activate venv using
source venv/bin/activate

# install necessary python packages
pip install requirements.txt

=====ENVIRONMENT SETUP=====

=====DATABASE SETUP=====

# make sure to delete database.db if there are any or if starting from scratch
python init_db.py

=====DATABASE SETUP=====

# run in port 8080
flask --app backend --debug run -p 8080