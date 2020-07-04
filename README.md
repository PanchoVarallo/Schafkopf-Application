1. Unbedingt Analyzer anpassen, d.h.
   1. Abstrahieren. Better Code.
   2. Momentan nur Wenz (Geyer könnte auch Crashen denke ich). Geyer/Solo hinzufügen. Außerdem: Gesamtstatistik der 
      Runde (Rufspiele/Farbsoli/...)
   3. Überschriften verbessern/Buttons hoch oder runter?
   4. Pop-Up bei Spieleintragung: Nur Spielstand ohne Ergebnisse.
2. Writer abstrahieren/SoloConfib bzw. RufspielConfig abstrahieren -> v.a. get_spieler_ids
3. Active bei allen Abfragen checken 
4. Kann man noch mehr Abstrahieren?
5. Hochzeit
6. Ramsch (Durchmarsch ab 91) -> 
   Möglichst abstrakt! (V.a. Spielstand Modal kann man abstrakt machen -> hmmm?)
7. Report erstellen

Falls ich noch Lust habe
- Code besser refaktoren
- Teilnehmer einrichten/bearbeiten, Runde einrichten/bearbeiten, Einzelspiele bearbeiten -> Dashboard
- Spielegenerator um Datenbank zu befüllen (Testdatenbank)
- Rundungen bei Statistik verbessern
- Make public on Github
 
 Wichtig für SQL:
 - Schema definition with alchemy: https://overiq.com/sqlalchemy-101/defining-schema-in-sqlalchemy-orm/
 - Create SQLite from command line: https://stackoverflow.com/questions/20155693/create-empty-sqlite-db-from-command-line
  
 Erklärungen zu Regeln:
- 10/20/50 (Hochzeit: 30)
- Kontra/Re: Bevor zweite Karte gefallen ist
- 6 Nixer: Pech gehabt
- Farbsolo: Ab drei Laufende
- Wenz/Geyer: Ab zwei Laufende
- Tout/Sie: Kein Schneider und kein Schwarz
- Ramsch: 
  - Punktgleichheit: Bei Punktgleichheit zählen die Anzahl der Stiche. Ist die Anzahl der Stiche ebenfalls gleich, 
    entscheidet die Anzahl der Trümpfe in den Stichen. Und wenn auch diese noch identisch sind, verliert derjenige, der 
    den höchsten Trumpf in seiner Karte hat (muss manuell angegeben werden)
  - Durchmarsch ab 91
 
 
 
