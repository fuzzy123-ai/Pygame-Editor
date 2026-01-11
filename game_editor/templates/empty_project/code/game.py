# game.py - Dein Spiel-Code
# Hier schreibst du die Logik für dein Spiel

player = get_object("player")

def update():
    # Bewegung mit Pfeiltasten
    if key_pressed("RIGHT") or key_pressed("D"):
        player.x += 4
    
    if key_pressed("LEFT") or key_pressed("A"):
        player.x -= 4
    
    if key_pressed("UP") or key_pressed("W"):
        player.y -= 4
    
    if key_pressed("DOWN") or key_pressed("S"):
        player.y += 4
    
    # Kollisionserkennung
    if player.collides_with("enemy1"):
        print_debug("Achtung! Kollision mit Enemy!")
