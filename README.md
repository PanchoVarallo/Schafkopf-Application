# Schafkopf-Application

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
MISSING
#### Creating a "Teilnehmer"
MISSING
#### Playing a game
MISSING
#### Seeing graphs and stats
MISSING

## Installation

The `Schafkopf-Application` was created with Python and the [Dash](https://dash.plotly.com/) framework. 

### Running it locally

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
5. Go to a browser and type in `http://127.0.0.1:8050/`. You will be asked for `username` and `password` and that's it.

### Implemented rules

We play `Rufspiel`, `Solo`, `Ramsch`, and `Hochzeit`, which is basically the used configuration in the small villages 
in the north-eastern region of Nuremberg. The calculation is based on the rules 
of [Sauspiel - Spielabrechnung](https://www.sauspiel.de/schafkopf-lernen/spielabrechnung).

### Contributing

PRs accepted! Feel free to add `Farbwenz`, `Farbgeyer`, `Bettel`, or whatever you want ...