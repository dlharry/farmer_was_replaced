clear()
from src import goto, N
wants = []
for i in range(N):
	wants.append({})
	for j in range(N):
		wants[i][j] = None
def do_plant(e):
	if get_ground_type() == Grounds.Grassland:
		till()
	plant(e)
	plant_type, (x, y) = get_companion()
	wants[x][y] = plant_type
	
while True:
	for i in range(N):
		for j in range(N):
			goto(i, j)
			if can_harvest():
				harvest()
			if get_entity_type() == None or get_ground_type() == Grounds.Grassland:
				if wants[i][j]:
					a, wants[i][j] = wants[i][j], None
					do_plant(a)
				else:
					do_plant(Entities.Carrot)