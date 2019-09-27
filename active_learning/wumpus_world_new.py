## Wumpus World ##
import random

class Mover():

	def __init__(self, position, world_size):
		self.position = position
		self.world_size = world_size

	def choose_action(self, actions, probabilities):
		random_number = random.uniform(0, 1)
		cumulative_probability = 0.0
		for action, probability in zip(actions, probabilities):
			cumulative_probability = cumulative_probability + probability
			if random_number < cumulative_probability:
				break
		return action

	def available_actions(self):
		if 1 < self.position[0] < self.world_size[0] and 1 < self.position[1] < self.world_size[1]:
			actions = ["up", "down", "left", "right", "stay"]
		if self.position[0] <= 1 and 1 < self.position[1] < self.world_size[1]:
			actions = ["up", "down", "right", "stay"]
		if self.position[0] >= self.world_size[0] and 1 < self.position[1] < self.world_size[1]:
			actions = ["up", "down", "left", "stay"]
		if 1 < self.position[0] < self.world_size[0] and self.position[1] <= 1:
			actions = ["up", "left", "right", "stay"]
		if 1 < self.position[0] < self.world_size[0] and self.position[1] >=  self.world_size[1]:
			actions = ["down", "left", "right", "stay"]		
		if self.position[0] <= 1 and self.position[1] <= 1:
			actions = ["up", "right", "stay"]
		if self.position[0] >= self.world_size[0] and self.position[1] <= 1:
			actions = ["up", "left", "stay"]
		if self.position[0] >= self.world_size[0] and self.position[1] >= self.world_size[1]:
			actions = ["down", "left", "stay"]
		if self.position[0] <= 1 and self.position[1] >= self.world_size[1]:
			actions = ["down", "right", "stay"]
		return actions

	def move(self, action):
		if action == "up":
			if self.position[1] < self.world_size[1]:
				self.position = (self.position[0], self.position[1] + 1)
		if action == "down":
			if self.position[1] > 1:
				self.position = (self.position[0], self.position[1] - 1)
		if action == "left":
			if self.position[0] > 1:
				self.position = (self.position[0] - 1, self.position[1])
		if action == "right":
			if self.position[0] < self.world_size[0]:
				self.position = (self.position[0] + 1, self.position[1])

	def move_randomly(self):
		actions = self.available_actions()
		probabilities = []
		for i in range(1, len(actions) + 1):
			probabilities.append(1/len(actions))
		action = self.choose_action(actions, probabilities)
		self.move(action)

	def sub_move_randomly(self, actions):
		valid_actions = self.available_actions()
		if set(actions) <= set(valid_actions):
			probabilities = []
			for i in range(1, len(actions) + 1):
				probabilities.append(1/len(actions))
			action = self.choose_action(actions, probabilities)
			self.move(action)

	def get_position(self):
		return self.position


class Wumpus(Mover):

	def __init__(self, position, world_size):
		Mover.__init__(self, position, world_size)

class Agent(Mover):

	def __init__(self, position, world_size, move_success_rate):
		Mover.__init__(self, position, world_size)
		self.move_success_rate = move_success_rate

	def move_uncertainly(self, action):
		valid_actions = self.available_actions()
		if action in valid_actions:
			actions = [action]
			for i in range(0, len(valid_actions)):
				if valid_actions[i] != action:
					actions.append(valid_actions[i])
			probabilities = [self.move_success_rate]
			for j in range(1, len(valid_actions)):
				probabilities.append((1 - self.move_success_rate)/(len(valid_actions)-1))
		real_action = self.choose_action(actions, probabilities)
		self.move(real_action)

	def move_randomly(self):
		actions = self.available_actions()
		probabilities = []
		for i in range(1, len(actions) + 1):
			probabilities.append(1/len(actions))
		action = self.choose_action(actions, probabilities)
		self.move_uncertainly(action)

	def sub_move_randomly(self, actions):
		valid_actions = self.available_actions()
		if set(actions) <= set(valid_actions):
			probabilities = []
			for i in range(1, len(actions) + 1):
				probabilities.append(1/len(actions))
			action = self.choose_action(actions, probabilities)
			self.move_uncertainly(action)

	def choose_exploit_action(self, state, q_table):
		actions = []
		q_values = []
		exploit_actions = []
		for key in q_table:
			if key[0] == state:
				actions.append(key[1])
				q_values.append(q_table[key])
		max_q_value = max(q_values)
		index = 0
		for q_value in q_values:
			if q_value == max_q_value:
				exploit_actions.append(actions[index])
			index = index + 1
		# probabilities = []
		# for i in range(1, len(exploit_actions) + 1):
		# 	probabilities.append(1/len(exploit_actions))
		# exploit_action = self.choose_action(exploit_actions, probabilities)
		# return exploit_action
		return exploit_actions

	# def epsilon_greedy(self, action, epsilon):
	# 	valid_actions = self.available_actions()
	# 	if action in valid_actions:
	# 		actions = [action]
	# 		probabilities = [1 - epsilon]
	# 		for valid_action in valid_actions:
	# 			if valid_action != action:
	# 				actions.append(valid_action)
	# 				probabilities.append((epsilon)/(len(valid_actions)-1))
	# 		greedy_action = self.choose_action(actions, probabilities)
	# 		self.move_uncertainly(action)

	def epsilon_greedy(self, exploit_actions, epsilon):
		valid_actions = self.available_actions()
		if set(exploit_actions) <= set(valid_actions):
			actions = []
			probabilities = []
			for exploit_action in exploit_actions:
				actions.append(exploit_action)
				probabilities.append((1 - epsilon)/len(exploit_actions))
			explore_actions = list(set(valid_actions) - set(exploit_actions))
			for explore_action in explore_actions:
				actions.append(explore_action)
				probabilities.append(epsilon/len(explore_actions))
			greedy_action = self.choose_action(actions, probabilities)
			self.move_uncertainly(greedy_action)
			return greedy_action


class World():

	def __init__(self, world_size, gold_pos, pits_pos, wumpus, agent):
		self.size = world_size
		self.gold_pos = gold_pos
		self.pits_pos = pits_pos
		self.wumpus = wumpus
		self.agent = agent
		self.breeze_pos = set()
		self.stench_pos = set()

	def check_valid_pos(self, position):
		if 1 <= position[0] <= self.size[0] and 1 <= position[1] <= self.size[1]:
			return True
		else:
			return False

	def get_breeze_pos(self):
		for position in self.pits_pos:
			if self.check_valid_pos((position[0], position[1] + 1)) == True:
				self.breeze_pos.add((position[0], position[1] + 1))
			if self.check_valid_pos((position[0], position[1] - 1)) == True:
				self.breeze_pos.add((position[0], position[1] - 1))
			if self.check_valid_pos((position[0] - 1, position[1])) == True:
				self.breeze_pos.add((position[0] - 1, position[1]))
			if self.check_valid_pos((position[0] + 1, position[1])) == True:
				self.breeze_pos.add((position[0] + 1, position[1]))
		return self.breeze_pos

	def get_stench_pos(self):
		self.stench_pos = set()
		wumpus_pos = self.wumpus.get_position()
		if self.check_valid_pos((wumpus_pos[0], wumpus_pos[1] + 1)) == True:
			self.stench_pos.add((wumpus_pos[0], wumpus_pos[1] + 1))
		if self.check_valid_pos((wumpus_pos[0], wumpus_pos[1] - 1)) == True:
			self.stench_pos.add((wumpus_pos[0], wumpus_pos[1] - 1))
		if self.check_valid_pos((wumpus_pos[0] - 1, wumpus_pos[1])) == True:
			self.stench_pos.add((wumpus_pos[0] - 1, wumpus_pos[1]))
		if self.check_valid_pos((wumpus_pos[0] + 1, wumpus_pos[1])) == True:
			self.stench_pos.add((wumpus_pos[0] + 1, wumpus_pos[1]))
		return self.stench_pos

class MDP(World):

	def __init__(self, world_size, gold_pos, pits_pos, wumpus, agent, agent_init_pos):
		World.__init__(self, world_size, gold_pos, pits_pos, wumpus, agent)
		self.agent_pre_pos = agent_init_pos

	def get_state_agentCell(self):
		position = self.agent.get_position()
		breeze = position in self.get_breeze_pos()
		gold = position == self.gold_pos
		pit = position in self.pits_pos
		stench = position in self.get_stench_pos()
		wumpus = position == self.wumpus.get_position()
		visited = 1
		return (1, stench, wumpus, visited)

	def init_state(self):
		state = []
		for column in range(1, self.size[0] + 1):
			for row in range(1, self.size[1] + 1):
				state.append((0, 0, 0, 0))
		column = self.agent.get_position()[0]
		row = self.agent.get_position()[1]
		state[(column-1)*self.size[1] + row - 1] = self.get_state_agentCell()
		return tuple(state)

	def update_state(self, state):
		state = list(state)
		column = self.agent.get_position()[0]
		row = self.agent.get_position()[1]
		state[(column-1)*self.size[1] + row - 1] = self.get_state_agentCell()
		if self.agent.get_position() != self.agent_pre_pos:
			column = self.agent_pre_pos[0]
			row = self.agent_pre_pos[1]
			flag = list(state[(column - 1)*self.size[1] + row - 1])
			flag[0] = 0
			state[(column-1)*self.size[1] + row - 1] = tuple(flag)
		self.agent_pre_pos = self.agent.get_position()
		# update stench after meet wumpus
		if self.agent.get_position() == self.wumpus.get_position():
			for i in range(len(state)):
				cell_state = state[i]
				cell_state = list(cell_state)
				cell_state[1] = 0
				cell_state = tuple(cell_state)
				state[i] = cell_state
			column = self.agent.get_position()[0]
			row = self.agent.get_position()[1]
			if column - 1 >= 1:
				flag = list(state[(column - 2)*self.size[1] + row - 1])
				flag[1] = 1
				state[(column - 2)*self.size[1] + row - 1] = tuple(flag)	
			if column + 1 <= self.size[0]:
				flag = list(state[(column)*self.size[1] + row - 1])
				flag[1] = 1
				state[(column)*self.size[1] + row - 1] = tuple(flag)		
			if row + 1 <= self.size[1]:
				flag = list(state[(column - 1)*self.size[1] + row])
				flag[1] = 1
				state[(column - 1)*self.size[1] + row] = tuple(flag)	
			if row - 1 >= 1:
				flag = list(state[(column - 1)*self.size[1] + row - 2])
				flag[1] = 1
				state[(column - 1)*self.size[1] + row - 2] = tuple(flag)			
		return tuple(state)

	def get_reward(self):
		position = self.agent.get_position()
		gold_pos = self.gold_pos
		pits_pos = self.pits_pos
		wumpus_pos = self.wumpus.get_position()
		if position == gold_pos and position != wumpus_pos:
			return 1
		elif position in pits_pos:
			return -1
		elif position == wumpus_pos:
			return -1
		else:
			return 0
	def expand_q_table(self, q_table, state):
		actions = self.agent.available_actions()
		for action in actions:
			if ((state, action) in q_table) == False:
				q_table[(state, action)] = 0
		return q_table

	def is_terminal(self):
		if self.agent.get_position() == self.gold_pos or self.agent.get_position() == self.wumpus.get_position() or self.agent.get_position() in self.pits_pos:
			return True
		else:
			return False





			













