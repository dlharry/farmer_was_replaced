N = get_world_size()
X, Y = get_pos_x(), get_pos_y()
def abs(x):
	if x>=0:
		return x
	return -x
def goto(x, y):
	global X
	global Y
	s, d = (x-X+N)%N, East
	if s*2>N:
		s, d = N-s, West
	for i in range(s):
		move(d)
	s, d = (y-Y+N)%N, North
	if s*2>N:
		s, d = N-s, South
	for i in range(s):
		move(d)
	X, Y = x, y

def reverse(arr):
	arr = list(arr)
	res = []
	for i in range(len(arr)):
		res.append(arr[len(arr)-1-i])
	return res