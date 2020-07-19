1. Refaktorieren und Testen
4. Make public on Github -> Maria Lackmustest

Falls ich noch Lust habe
- Tests für Validator - Writer/Analyzer - Frontend
- Übersichtsreport erstellen
- Teilnehmer einrichten/bearbeiten, Runde einrichten/bearbeiten, Einzelspiele bearbeiten -> Dashboard
- Rundungen bei Statistik verbessern
- Extra Tab für 'Falsch ausgeteilt'
- Statistik Kontriert und Re abhängig von der Möglichkeit an Kontras und Res machen (nicht abhängig von Einzelspielen)
 
 Wichtig für SQL:
 - Schema definition with alchemy: https://overiq.com/sqlalchemy-101/defining-schema-in-sqlalchemy-orm/
 - Create SQLite from command line: https://stackoverflow.com/questions/20155693/create-empty-sqlite-db-from-command-line
  
 Erklärungen zu Regeln:
- 10/20/50 (Hochzeit: 30)
- Kontra/Re: Bevor zweite Karte gefallen ist
- 6 Nixer: Pech gehabt, es wird trotzdem gespielt
- Farbsolo: Ab drei Laufenden
- Wenz/Geyer: Ab zwei Laufenden
- Tout/Sie: Kein Schneider und kein Schwarz
- Ramsch: 
  - Hat ein Spieler am Ende des Spiels mindestens 91 Augen, ist ihm ein Durchmarsch gelungen und er bekommt von den 
    anderen drei Spielern jeweils 50 Cent (im Tarif 10-20-50) (Leger bleiben, es gibt keine Jungfrauen)
  - Punktgleichheit: Bei Punktgleichheit zählt die Anzahl der Stiche. Ist die Anzahl der Stiche ebenfalls gleich, 
    entscheidet die Anzahl der Trümpfe in den eigenen Stichen. Und wenn auch diese noch identisch sind, verliert 
    derjenige, der den höchsten Trumpf in seinen Stichen hat. Danach entscheidet, wer das höchste Ass hat (in der 
    Reihenfolge Eichel, Gras, Herz, Schellen)