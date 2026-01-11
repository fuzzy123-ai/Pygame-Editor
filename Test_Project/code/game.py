# Code für object_6
# Hier schreibst du die Logik für dieses Objekt

player = get_object("object_6")

def update():
	if key_pressed("RIGHT") or    	key_pressed("D"):
		player.x += 4
 	if key_pressed("LEFT") or key_pressed("A"):
		player.x -= 4  
