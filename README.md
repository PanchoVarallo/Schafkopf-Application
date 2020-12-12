# Schafkopf-Application
[![Build Status](https://travis-ci.com/PanchoVarallo/Schafkopf-Application.svg?branch=master)](https://travis-ci.com/github/PanchoVarallo/Schafkopf-Application)
[![codecov](https://codecov.io/gh/PanchoVarallo/Schafkopf-Application/branch/master/graph/badge.svg)](https://codecov.io/gh/PanchoVarallo/Schafkopf-Application)
[![Heroku](https://heroku-badge.herokuapp.com/?app=heroku-badge)](https://schafkopf-app.herokuapp.com/)

[Schafkopf](https://en.wikipedia.org/wiki/Schafkopf) is the most popular card game in Bavaria. With this application, 
you can record results of your physical [Schafkopf](https://en.wikipedia.org/wiki/Schafkopf) round in an 
[SQLite](https://www.sqlite.org/index.html) database.  

Why should I do this instead of using pen and paper? 
- The `Schafkopf-Application` calculates the results immediately.
- You can access wonderful graphs illustrating the results.
- You can access comprehensive stats analyzing gaming behavior of the players.
- You have a database with all the results for doing further analysis.

## Manual

Going through these `gif` animations covers all the features of the `Schafkopf-Application`.

#### Creating a "Runde"
MISSING. See Issue!

#### Creating a "Teilnehmer"
MISSING. See Issue!

#### Playing a game
MISSING. See Issue!

#### Seeing graphs and stats
MISSING. See Issue!

## Installation

The `Schafkopf-Application` was created with Python and the [Dash](https://dash.plotly.com/) framework. 
You can run the application locally and access it via your browser:

1. Clone `Schafkopf-Application` and go to the `schafkopf` directory.
2. Create a `conda` environment and install the requirements via `sudo` and `pip`.
```
conda create --name schafkopf
conda activate schafkopf
conda install pip
sudo apt-get install libpq-dev
pip install -r requirements.txt
```
3. Define database setting in `settings.ini`. Do not change `[Database]` but adjust `username` and `password` 
for authentication. Run `python init.py` to init the schema in the [SQLite](https://www.sqlite.org/index.html) 
database called `schafkopf.db`.
4. Start the application with 
```
python -m app
```
5. Go to a browser and type in `http://127.0.0.1:8050/`. You will be asked for `username` and `password`.

## Implemented rules

We play `Rufspiel`, `Solo`, `Ramsch`, and `Hochzeit`, which is basically the used configuration in the small villages 
in the north-eastern region of Nuremberg. The calculation is based on the rules 
of [Sauspiel - Spielabrechnung](https://www.sauspiel.de/schafkopf-lernen/spielabrechnung).

## Remarks
- Tests are only written for the backend. The test coverage above refers to the backend. 
- You can deploy this dash application to [Heroku](https://dashboard.heroku.com/):
  - Deploy the code: [https://dash.plotly.com/deployment](https://dash.plotly.com/deployment)
  - You cannot use the [SQLite](https://www.sqlite.org/index.html) database on Heroku. 
    Instead, you can use a [PostgreSQL for Heroku](https://www.heroku.com/postgres).
  - After defining the PostgreSQL, you adjust the ``settings.ini`` (self-explainable) and run `python init.py`
    to initialize the empty PostgreSQL on Heroku. See ``init.py`` for details.
  - Finally, you define ``Config Vars`` on Heroku:
    - DATABASE_URL - ``URL to Heroku PostgreSQL``. See ``session.py`` for details.
    - LANG - ``de_DE.utf8``
    - TZ - ``Europe/Berlin``
    

