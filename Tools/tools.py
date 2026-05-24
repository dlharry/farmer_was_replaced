def use_in_a_area(f,x,y):
	for i in range(x-1):
		for j in range(y-1):
			f()
			move(North)
		f()
		for j in range(y-1):
			move(South)
		move(East)
	for j in range(y-1):
		f()
		move(North)
	f()
	for j in range(y-1):
		move(South)
	for i in range(x-1):
		move(West)

def cover(f):
	size = get_world_size()
	for i in range(size):
		for j in range(size):
			f()
			move(North)
		move(East)

def global_multi_use(f):
	def _f():
		for i in range(get_world_size()):
			f()
			move(East)
	goto(0,0)
	for i in range(get_world_size()):
		while True:
			if spawn_drone(_f):
				break
			move(North)

def __move(x,y):
	while x > 0:
		move(East)
		x -= 1
	while x < 0:
		move(West)
		x += 1
	while y > 0:
		move(North)
		y -= 1
	while y < 0:
		move(South)
		y += 1
def dis(P1, P2):
	(x1, y1) = P1
	(x2, y2) = P2
	return abs(x1 - x2) + abs(y1 - y2)

def goto(x, y):
	size = get_world_size()
	L = [(x + size, y + size), (x + size, y - size), (x - size, y + size), (x, y - size)]
	P = (x, y)
	P0 = (get_pos_x(), get_pos_y())
	D = dis(P0, P)
	for _P in L:
		if dis(P0, _P) < D:
			D = dis(P0, _P)
			P = _P
	(_x, _y) = P
	(x0, y0) = P0
	__move(_x - x0, _y - y0)

def pack(_f, Arg):
	def work():
		_f(Arg)
	return work
def wait():
	while True:
		if(num_drones() == 1):
			break
def rev(dir):
	if(dir == East):
		return West
	if(dir == North):
		return South
	if(dir == West):
		return East
	if(dir == South):
		return North
def at_edge(dir):
	if(dir == East):
		return get_pos_x() == get_world_size() - 1
	if(dir == North):
		return get_pos_y() == get_world_size() - 1
	if(dir == West):
		return get_pos_x() == 0
	if(dir == South):
		return get_pos_y() == 0