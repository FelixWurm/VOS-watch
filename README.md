# VOS-watch
 
This is a Program to track the dearture times of Buslines in Onsabrück from varios Stations.  

## Ideeen:
- Tabelle für:
    - Buslinien (ermöglicht auch das nachträgliche ändern von nummern bei fahrplanänderung), wie oft Ausgefallen 

    - Abgefahrene Buse, ID -> ID vom VOS system, originale abfahrtszeit, neue abfahrtsszeit (am besten in UTC), verspätung, first_seen (also wann hat die software den bus zu erst gesehen), writs (wie oft wurde die zeile geaänder), optinal max_delay und min_delay (natürlich jeweils nur im gesehenen Zeitfenster), WICHTIG auch haltestelle von der Gemessen wird (sollten es doch verschiedene optinen geben in der zukunft)

    - Ziele (name, ID(KEY),)

- möglichkeit die letzten / neusten elemente zu bekommen? elemente der letzten stunde? originale oder echte abfahrtszeit?
- hinzufügeb Bus fällt aus (dann natürlich nicht mitzählen)
- Dynamische wahl des zeitfensterns bei sehr hoher verspätung

Some of the information to the hafas protocoll come from this side:
https://github.com/public-transport/transport-apis/blob/v1/data/de/vos-hafas-mgate.json