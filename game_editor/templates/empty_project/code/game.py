# game.py - Dein Spiel-Code
# Hier schreibst du die Logik für dein Spiel

spieler = hole_objekt("player")

definiere aktualisiere():
    # Bewegung mit Pfeiltasten
    wenn taste_gedrückt("RECHTS") oder taste_gedrückt("D"):
        spieler.x += 4
    
    wenn taste_gedrückt("LINKS") oder taste_gedrückt("A"):
        spieler.x -= 4
    
    wenn taste_gedrückt("HOCH") oder taste_gedrückt("W"):
        spieler.y -= 4
    
    wenn taste_gedrückt("RUNTER") oder taste_gedrückt("S"):
        spieler.y += 4
    
    # Kollisionserkennung
    wenn spieler.kollidiert_mit("enemy1"):
        drucke_debug("Achtung! Kollision mit Enemy!")
