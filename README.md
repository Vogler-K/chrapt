# Projekt: 'chrapt' (Modularer Paketmanager)
## Team: Vogler Konstantin (solo)
## Konzept
"chrapt" installiert Debian/Ubuntu-Pakete isoliert in autarken Sandboxen ("Boxes") – komplett ohne externe Python-Abhängigkeiten.
Da jede Box ihre eigenen Libraries mitbringt, läuft alte Software problemlos neben neuer, ohne das Host-System zu manipulieren. Gestartet wird per bubblewrap (bwrap) mit Shared-System-Ressourcen (Wayland, Netzwerk). Für Transport oder Lagerung werden Boxen als .tar.gz eingefroren. Bei einer Neu-Installation in denselben Ordner wird dieser automatisch überschrieben.
##Ziele
+ Isolierung: Volle Isolation über bwrap (kein Root für Apps nötig).
+ Portabilität: Boxen als Archiv einfach auf andere PCs verschieben.
+ Multiversion: Parallele Versionen derselben Software ausführbar.
+ PATH-Integration: Wrapper-Skripte landen direkt im Benutzer-$PATH.
## Befehls-Übersicht
+ chrapt tree <packet>: Analysiert und zeichnet den Dependency-Baum (mit Zyklenschutz).
+ chrapt install <folder> <packets>: Lädt .deb-Dateien, entpackt sie via dpkg -x und baut die Wrapper-Skripte.
+ chrapt list: Zeigt alle "live" (entpackten) und "packed" (archivierten) Boxen.
+ chrapt bundle/scatter <folder>: Friert eine Live-Box ein (erzeugt .tar.gz, löscht Ordner) bzw. taut sie wieder auf.
+ chrapt remove <folder>: Löscht eine Box (Ordner + Archiv) und fegt alle Aliase aus dem PATH.
## Meilensteine
1. 'chrapt tree': Dependency analysis und checken ob das Paket verarbeitbar ist
- Tree anzeigen funktioner, grunsätzlich sind alle Pakete verarbeitbar manche Sonderpakete wie systemd werden gefiltert das kann aber mit --advanced überschrieben werden
2. 'chrapt install': Die größte Hürde, das Downloaden des Paketes und allen Dependencies von den Debian Mirrors und alles in ein chrapt lesbares .tar.zst packen
- Verwenden von Z-Standard ist ein Python unnötig komplexer als Gzip, deswegen bin ich umgestiegen
3. 'chrapt pack' & 'chrapt unpack': Zum ent-, und packen des Live-Ordners in das .tar.zst
- Umbenannt in bundle und scatter
4. Weiterer Weg: 'chrapt port': Zum übertragen der geschrieben Daten, wie Logs, Datenbanken usw.,zu einer neuen Version
- Nicht weiter nötig, neue Versionen können einfach mit install installiert werden, alte sind aufgrund von apt nicht möglich/kompliziert THEORETISCH funktioniert chrapt install BOX PACKET=VERSION, meistens ist aber nur die neueste Version zum download von apt freigegeben
<p style="font-size: 0.4em; color: lightgray;">Diese Beschreibung und andere Beschreibende Texte sind teilweise KI generiert und könnten Fehler enthalten</p>
