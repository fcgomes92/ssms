# Simples Storage Management System

[![CircleCI](https://img.shields.io/circleci/project/github/RedSparr0w/node-csgo-parser.svg)](https://circleci.com/gh/fcgomes92/ssms)
[![Github All Releases](https://img.shields.io/github/downloads/fcgomes92/ssms/total.svg)](https://github.com/fcgomes92/ssms)
[![GitHub tag](https://img.shields.io/github/tag/fcgomes92/ssms.svg)](https://github.com/fcgomes92/ssms/tags) 
[![GitHub release](https://img.shields.io/github/release/fcgomes92/ssms.svg)](https://github.com/fcgomes92/ssms/releases)  

A Simple Storage Management System focused on managing orders from small restaurants / cookers.

Aims to help a cooker manage orders and clients, and the amount of ingredients used in one or more orders.

---

Test / First User: [Ovelha Negra](https://fb.com/ovelhanegraveg)

----

### Using:

* Python 3.6.x
* [Falcon](https://falcon.readthedocs.io/en/stable/)
* [Marshmellow](http://marshmallow.readthedocs.io/)
* [SQLAlchemy](https://www.sqlalchemy.org/)
* [Python Decouple](https://pypi.python.org/pypi/python-decouple)
* [PyTest](https://docs.pytest.org/en/latest/)

More about versions in the file: [requirements.txt](/requirements.txt)

---

### First steps:

* Clone this repository

```
git clone https://github.com/fcgomes92/ssms
```

* Create a virtual environment 

```
cd ssms
virtualenv .env
```

---

### How to run the api (simple method):

* On the first run or after an update you sould run:

```
python config.py
```

* Then to start the server on 127.0.0.1:8000 run:

```
python run.py
```

---

### How to run the api (detailed):


* Activate the virtualenv

```
source .env/bin/activate
```


* Create a .env file, you can follow the [env.mock](/ssms/env.mock) to get all the available configuration variables 
(The .env should be inside the ssms folder) 

* Install all the requirements 

```
pip install -r requirements.txt
```

* Run the api

```
gunicorn --reload 'ssms.app:create_app()'
```

---

To run tests you should run:

```
DATABASE_URI=sqlite:///:memory: pytest tests/test_app.py
```