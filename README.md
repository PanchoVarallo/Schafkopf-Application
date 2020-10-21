ToDos:
- add a Dashboard where we select "Runde" and get "Einzelspiele" with time tag. Now we can see the details of the game
  and delete Einzelspiele (exact desgin has to be invented)
- "Punkteconfig" bei insert_runde(...) einbauen. Namen des default "Punkteconfig" auf "default" ändern.
- build recognizion of six players in the last two games (or even seven in the last three games)
- publish on github with short docu, automatic tests (travis) and default sqlite (remove password protection)
 
 
 In die Dokumentation:
 
 Hilfreiche Websites beim Projekt:
 - Schema definition with alchemy: https://overiq.com/sqlalchemy-101/defining-schema-in-sqlalchemy-orm/
 - Create SQLite from command line: https://stackoverflow.com/questions/20155693/create-empty-sqlite-db-from-command-line
  
 Erklärungen zu implementierten Regeln:
- Laufende/Schneider/Schwarz:10, Rufspiel: 20, Hochzeit:30, Solo: 50 -> Kann über Punkteconfig konfiguriert werden
- Wenz/Geier: Ab zwei Laufenden -- Farbsolo: Ab drei Laufenden
- Tout/Sie: Kein Schneider und kein Schwarz
- Ramsch: 
  - Hat ein Teilnehmer am Ende des Spiels mindestens 91 Augen, ist ihm ein Durchmarsch gelungen und er bekommt von den 
    anderen drei Teilnehmern jeweils 50 Cent (im Tarif 10-20-50) (Leger bleiben, es gibt keine Jungfrauen)

Sinnvolle Regeln für Spielablauf:
- Kontra/Re: Bevor zweite Karte gefallen ist
- Sechs Nixer: Es wird trotzdem gespielt
- Unterspielen bei mindestens 4 von der Ruffarbe -> Nur beim Rauskommen. Danach frei.
- Reihenfolge der Soli: Geyer, Wenz, Farbsolo. Bei Farbsolo: Wer früher sitzt, außer Herz Solo
- Ramsch Punktgleichheit: 
    Bei Punktgleichheit zählt die Anzahl der Stiche. Ist die Anzahl der Stiche ebenfalls gleich, 
    entscheidet die Anzahl der Trümpfe in den eigenen Stichen. Und wenn auch diese noch identisch sind, verliert 
    derjenige, der den höchsten Trumpf in seinen Stichen hat. Danach entscheidet, wer das höchste Ass hat (in der 
    Reihenfolge Eichel, Gras, Herz, Schellen)