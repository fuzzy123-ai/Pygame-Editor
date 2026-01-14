platform = get_object("object_13")

platform_speed = 2
platform_direction = -1
platform_start_x = 672
platform_end_x = 800

# Y-Position fixieren (wird automatisch nach jedem Update zurückgesetzt)
lock_y_position(platform, platform.y)

def update():
    global platform_direction
    
    # Bewegung hin und her mit Kollisionsbehandlung
    dx = platform_speed * platform_direction
    dy = 0
    
    on_ground, collision_x, collision_y = move_with_collision(platform, dx, dy)
    
    # Andere Objekte wegdrücken
    if dx != 0:
        push_objects(platform, dx, dy)
    
    # Umkehren wenn am Ende oder bei Kollision
    if platform.x >= platform_end_x or collision_x:
        platform_direction = -1
    elif platform.x <= platform_start_x or collision_x:
        platform_direction = 1