bär = hole_objekt("object_15")

# Geschwindigkeit
geschwindigkeit = 3
schwerkraft = 0.5
geschwindigkeit_y = 0
auf_boden = falsch

funktion aktualisiere():
    global geschwindigkeit_y, auf_boden
    
    # Horizontal-Bewegung
    dx = 0
    wenn taste_gedrückt("LINKS"):
        dx = -geschwindigkeit
    wenn taste_gedrückt("RECHTS"):
        dx = geschwindigkeit
    
    # Schwerkraft
    wenn nicht auf_boden:
        geschwindigkeit_y += schwerkraft
    
    # Bewegung mit automatischer Kollisionsbehandlung
    auf_boden, kollision_x, kollision_y = bewege_mit_kollision(bär, dx, geschwindigkeit_y)
    
    # Wenn auf Boden, Geschwindigkeit zurücksetzen
    wenn auf_boden:
        geschwindigkeit_y = 0
    
    # Sprung - taste_gedrückt für kontinuierliches Springen
    wenn taste_gedrückt("SPACE") und auf_boden:
        geschwindigkeit_y = -10
        auf_boden = falsch