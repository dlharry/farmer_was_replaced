def farm():
	for i in range(get_world_size()):
		for y in range(get_world_size()):
			if can_harvest():
				harvest()
			if get_pos_x() % 2 == 0 and get_pos_y() % 2 == 0:
				plant(Entities.Tree)
				use_item(Items.Fertilizer)
			elif get_pos_x() % 2 == 1 and get_pos_y() % 2 == 1:
				plant(Entities.Tree)
				use_item(Items.Fertilizer)
			else:
				plant(Entities.Bush)
				use_item(Items.Fertilizer)

			move(North)
		move(East)
while True:
	farm()