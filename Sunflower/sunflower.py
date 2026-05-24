def mmove(x, y):
	# 智能移动函数，选择最短路径，利用环形边界
	current_x = get_pos_x()
	current_y = get_pos_y()
	world_size = get_world_size()

	# 智能选择水平移动方向
	if x != current_x:
		east_distance = (x - current_x) % world_size
		west_distance = (current_x - x) % world_size

		if east_distance <= west_distance:
			# 向东移动更短或相等
			for _ in range(east_distance):
				move(East)
		else:
			# 向西移动更短
			for _ in range(west_distance):
				move(West)

	# 智能选择竖直移动方向
	if y != current_y:
		north_distance = (y - current_y) % world_size
		south_distance = (current_y - y) % world_size

		if north_distance <= south_distance:
			# 向北移动更短或相等
			for _ in range(north_distance):
				move(North)
		else:
			# 向南移动更短
			for _ in range(south_distance):
				move(South)

def tmove(xy):
	mmove(xy[0], xy[1])

def water():
	if get_water() < 0.75:
		use_item(Items.Water)

def pp(p):
	water()
	plant(p)

def drone_plant_row(start_y, end_y, direction):
	# 无人机负责种植指定行范围的向日葵
	for y in range(start_y, end_y, direction):
		if y % 2 == 0:
			for x in range(get_world_size()):
				mmove(x, y)
				if get_entity_type() != Entities.Sunflower:
					harvest()
				if get_ground_type() == Grounds.Grassland:
					till()
				water()
				plant(Entities.Sunflower)
		else:
			for x in range(get_world_size() - 1, -1, -1):
				mmove(x, y)
				if get_entity_type() != Entities.Sunflower:
					harvest()
				if get_ground_type() == Grounds.Grassland:
					till()
				water()
				plant(Entities.Sunflower)

def drone_harvest_by_size(min_size, positions):
	# 无人机负责收割指定大小的向日葵
	for pos in positions:
		tmove(pos)
		if get_entity_type() == Entities.Sunflower and measure() >= min_size:
			harvest()

def collect_sunflower_positions():
	# 获取世界大小和可用无人机数量
	world_size = get_world_size()
	available_drones = max_drones()

	if available_drones <= 1:
		# 单无人机扫描
		cutDi = {}
		for y in range(world_size):
			if y % 2 == 0:
				for x in range(world_size):
					mmove(x, y)
					record_position_to_dict(cutDi)
			else:
				for x in range(world_size - 1, -1, -1):
					mmove(x, y)
					record_position_to_dict(cutDi)
		return cutDi

	# 多无人机并发扫描 - 通过参数传递字典
	all_cutDi = {}  # 主程序存储所有扫描结果
	drone_handles = []  # 存储无人机句柄

	# 计算每架无人机负责的行数
	rows_per_drone = world_size // available_drones
	remaining_rows = world_size % available_drones

	# 先创建所有其他无人机，再执行主程序任务
	start_row = 0
	main_drone_result = None  # 存储主程序的扫描结果

	for i in range(available_drones):
		end_row = start_row + rows_per_drone
		if i < remaining_rows:
			end_row += 1

		if start_row < world_size:
			if i == 0:
				# 主程序无人机负责第一部分，稍后执行
				main_start_row = start_row
				main_end_row = end_row
			else:
				# 为其他无人机创建扫描任务
				def create_scan_task(start_y, end_y):
					def task():
						local_cutDi = {}
						for y in range(start_y, end_y):
							if y % 2 == 0:
								for x in range(world_size):
									mmove(x, y)
									record_position_to_dict(local_cutDi)
							else:
								for x in range(world_size - 1, -1, -1):
									mmove(x, y)
									record_position_to_dict(local_cutDi)
						return local_cutDi  # 返回扫描结果
					return task

				drone_handle = spawn_drone(create_scan_task(start_row, end_row))
				if drone_handle != None:
					drone_handles.append(drone_handle)

		start_row = end_row

	# 主程序无人机执行自己的扫描任务
	main_drone_result = {}
	for y in range(main_start_row, main_end_row):
		if y % 2 == 0:
			for x in range(world_size):
				mmove(x, y)
				record_position_to_dict(main_drone_result)
		else:
			for x in range(world_size - 1, -1, -1):
				mmove(x, y)
				record_position_to_dict(main_drone_result)

	# 等待所有其他无人机完成并收集结果
	for drone_handle in drone_handles:
		scan_result = wait_for(drone_handle)  # 获取无人机的返回值

		# 合并扫描结果
		for size in scan_result:
			if size in all_cutDi:
				# 合并位置字典
				for pos in scan_result[size]:
					all_cutDi[size][pos] = True
			else:
				all_cutDi[size] = {}
				for pos in scan_result[size]:
					all_cutDi[size][pos] = True

	# 合并主程序的扫描结果
	if main_drone_result != None:
		for size in main_drone_result:
			if size in all_cutDi:
				# 合并位置字典
				for pos in main_drone_result[size]:
					all_cutDi[size][pos] = True
			else:
				all_cutDi[size] = {}
				for pos in main_drone_result[size]:
					all_cutDi[size][pos] = True

	return all_cutDi

def record_position_to_dict(cutDi):
	# 记录向日葵位置到字典中
	if get_entity_type() == Entities.Sunflower:
		size = measure()
		pos = (get_pos_x(), get_pos_y())
		if size in cutDi:
			cutDi[size][pos] = True
		else:
			cutDi[size] = {pos: True}

def get_available_drones():
	# 获取当前可用无人机数量
	max_available = max_drones()
	current_active = num_drones()
	return max_available - current_active

def wait_for_any_drone(active_drone_handles):
	# 等待任意一个无人机完成，返回剩余的活跃无人机句柄
	if not active_drone_handles:
		return active_drone_handles

	# 等待第一个完成的无人机
	completed_drone = wait_for(active_drone_handles[0])

	# 移除已完成的无人机句柄
	remaining_handles = active_drone_handles[1:]

	# 返回剩余的活跃无人机句柄
	return remaining_handles

def create_single_harvest_task(pos):
	# 为单个向日葵位置创建收割任务
	def task():
		tmove(pos)
		# 双重检查：确保向日葵仍然存在且可收割
		if get_entity_type() == Entities.Sunflower:
			harvest()
		return True  # 返回任务完成状态
	return task

def multi_drone_plant_sunflower():
	# 获取世界大小和可用无人机数量
	world_size = get_world_size()
	available_drones = max_drones()

	if available_drones <= 1:
		# 如果只有一架无人机，使用原始方法
		snakemove(plantsunflower_logic)
		return

	# 计算每架无人机负责的行数（主无人机也参与工作）
	rows_per_drone = world_size // available_drones
	remaining_rows = world_size % available_drones

	# 先创建所有其他无人机，再执行主程序任务
	start_row = 0
	for i in range(available_drones):
		end_row = start_row + rows_per_drone
		if i < remaining_rows:
			end_row += 1

		if start_row < world_size:
			if i == 0:
				# 记录主无人机负责的行范围，稍后执行
				main_start_row = start_row
				main_end_row = end_row
			else:
				# 为其他无人机创建种植任务
				def create_plant_task(start_y, end_y):
					def task():
						drone_plant_row(start_y, end_y, 1)
					return task

				spawn_drone(create_plant_task(start_row, end_row))

		start_row = end_row

	# 主无人机执行自己的种植任务
	drone_plant_row(main_start_row, main_end_row, 1)

def multi_drone_harvest_sunflower():
	# 改进的多无人机收割系统：一机一葵模式
	cutDi = collect_sunflower_positions()
	available_drones = max_drones()

	if available_drones <= 1:
		# 如果只有一架无人机，主程序直接收割
		for size in range(15, 6, -1):
			if size in cutDi:
				for pos in cutDi[size]:
					tmove(pos)
					if get_entity_type() == Entities.Sunflower:
						harvest()
		return

	# 收集所有向日葵位置，按尺寸从大到小排序，只存储坐标
	all_positions = []
	for size in range(7, 16, 1):
		if size in cutDi:
			for pos in cutDi[size]:
				all_positions.append(pos)

	if not all_positions:
		return

	# 活跃无人机句柄列表
	active_drone_handles = []
	harvested_count = 0
	total_count = len(all_positions)

	quick_print("开始收割 " + str(total_count) + " 个向日葵，使用一机一葵模式")

	# 为每个向日葵位置创建独立任务
	while len(all_positions) > 0:
		# 等待可用无人机
		while get_available_drones() <= 0:
			if active_drone_handles:
				active_drone_handles = wait_for_any_drone(active_drone_handles)
				harvested_count += 1
			else:
				# 如果没有活跃无人机，稍等片刻
				pass

		# 创建新的收割任务
		harvest_task = create_single_harvest_task(all_positions.pop())
		drone_handle = spawn_drone(harvest_task)

		if drone_handle != None:
			active_drone_handles.append(drone_handle)
		else:
			# 如果创建失败，直接收割
			tmove(pos)
			if get_entity_type() == Entities.Sunflower:
				harvest()
				harvested_count += 1

def plantsunflower_logic():
	# 单个格子的种植逻辑
	if get_entity_type() != Entities.Sunflower:
		harvest()
	if get_ground_type() == Grounds.Grassland:
		till()
	water()
	plant(Entities.Sunflower)

def snakemove(g, arg=None):
	# 原始的蛇形移动函数
	for y in range(get_world_size()):
		if y % 2 == 0:
			for x in range(get_world_size()):
				mmove(x, y)
				if arg == None:
					g()
				else:
					g(arg)
		else:
			for x in range(get_world_size() - 1, -1, -1):
				mmove(x, y)
				if arg == None:
					g()
				else:
					g(arg)

def plantsunflower_multi_drone():
	# 主要的多无人机向日葵种植函数

	# 第一步：多无人机并发种植
	multi_drone_plant_sunflower()

	# 等待种植完成
	while num_drones() > 1:
		pass  # 等待其他无人机完成

	# 第二步：多无人机并发收割成熟的向日葵
	multi_drone_harvest_sunflower()

	# 等待收割完成
	while num_drones() > 1:
		pass  # 等待其他无人机完成

	quick_print("多无人机向日葵种植和收割完成")

def plantsunflower():
	# 原始的单无人机向日葵种植函数，作为备用
	def g():
		if get_entity_type() != Entities.Sunflower:
			harvest()
		if get_ground_type() == Grounds.Grassland:
			till()
		plant(Entities.Sunflower)

	snakemove(g)

	def f(cutDi):
		if measure() in cutDi:
			cutDi[measure()].add((get_pos_x(), get_pos_y()))
		else:
			cutDi[measure()] = {(get_pos_x(), get_pos_y())}

	cutDi = {}
	snakemove(f, cutDi)

	for i in range(15, 6, -1):
		if i in cutDi:
			for n in cutDi[i]:
				tmove(n)
				harvest()

if __name__ == "__main__":
	# 使用多无人机版本
		plantsunflower_multi_drone()