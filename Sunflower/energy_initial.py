N = get_world_size()
def farm():
	global N
	petal_counter = 15
	for i in range(N):
		for y in range(N):
			if can_harvest():
				harvest()
			if get_ground_type() == Grounds.Grassland:
				till()
			plant(Entities.Sunflower)
			move(North)
		move(East)
	while petal_counter >= 7:
		for i in range(N):
			for y in range(N):
				if can_harvest():
					if measure() == petal_counter:
						harvest()
				move(North)
			move(East)
		petal_counter -= 1
while True:
	farm()
			