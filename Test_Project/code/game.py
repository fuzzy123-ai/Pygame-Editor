bear = get_object("object_15")

# Geschwindigkeit
speed = 3
gravity = 0.5
velocity_y = 0
on_ground = False

def update():
    global velocity_y, on_ground
    
    # Horizontal-Bewegung
    dx = 0
    if key_pressed("LEFT"):
        dx = -speed
    if key_pressed("RIGHT"):
        dx = speed
    
    # Schwerkraft
    if not on_ground:
        velocity_y += gravity
    
    # Bewegung mit automatischer Kollisionsbehandlung
    on_ground, collision_x, collision_y = move_with_collision(bear, dx, velocity_y)
    
    # Wenn auf Boden, Geschwindigkeit zurücksetzen
    if on_ground:
        velocity_y = 0
    
    # Sprung
    if key_down("SPACE") and on_ground:
        velocity_y = -10
        on_ground = False 