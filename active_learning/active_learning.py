import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn import metrics
from wumpus_world_new import *
import matplotlib.pyplot as plt
from math import *

max_episode = 10000
episode_duration = 16
episode = 1
gamma = 0.95
epsilon = 0.1
alpha = 0.01
q_table = dict()
loss_list = []
states = set()
states_1000 = set()
state_number = []
iterations = 0
x = []
y = []

while episode <= max_episode:
	dataset = []
	time = 1
	while time < 16:
		data = []
		if time == 1:
			agent = Agent((1,1), (4,4), 0.9)
			wumpus = Wumpus((1,3), (4,4))
			world = MDP((4,4), (2,3), [(3,1), (3,3), (4,4)], wumpus, agent, (1,1))
			state = world.init_state()
			states.add(state)
			data.append(state)
			reward = world.get_reward()
			if world.is_terminal() == True:
				data.append(reward)
				dataset.append(data)	
				# if episode > 9000:
				# 	x.append(state)
				# 	y.append("stay")
				# 	states_1000.add(state)		
				break
			q_table = world.expand_q_table(q_table, state)
			exploit_actions = agent.choose_exploit_action(state, q_table)
			action = agent.epsilon_greedy(exploit_actions, epsilon)
			data.append(action)
			if episode > 9000:
				x.append(state)
				y.append(action)
				states_1000.add(state)
			data.append(reward)
			wumpus.move_randomly()
			state = world.update_state(state)
			states.add(state)
			data.append(state)
		else:
			data.append(state)
			reward = world.get_reward()
			if world.is_terminal() == True:
				data.append(reward)
				dataset.append(data)	
				# if episode > 9000:
				# 	x.append(state)
				# 	y.append("stay")
				# 	states_1000.add(state)		
				break
			q_table = world.expand_q_table(q_table, state)
			exploit_actions = agent.choose_exploit_action(state, q_table)
			action = agent.epsilon_greedy(exploit_actions, epsilon)
			data.append(action)
			if episode > 9000:
				x.append(state)
				y.append(action)
				states_1000.add(state)
			data.append(reward)
			wumpus.move_randomly()
			state = world.update_state(state)
			states.add(state)
			data.append(state)
			if time == 15:
				q_table = world.expand_q_table(q_table, state)
		dataset.append(data)
		time = time + 1
		state_number.append(len(states))
		iterations = iterations + 1
	loss = 0
	for i in range(len(dataset) - 1, -1, -1):
		if len(dataset[i]) < 4:
			current_state = dataset[i][0]
			current_reward = dataset[i][1]
			if ((current_state, "stay") in q_table) == False:
				q_table[(current_state, "stay")] = 0
			q_table[(current_state, "stay")] = (1 - alpha) * q_table[(current_state, "stay")] + alpha * current_reward
			loss = loss + (current_reward - q_table[(current_state, "stay")])**2
		else:
			current_state = dataset[i][0]
			current_action = dataset[i][1]
			current_reward = dataset[i][2]
			next_state = dataset[i][3]
			next_q_values = []
			for key in q_table:
				if key[0] == next_state:
					next_q_values.append(q_table[key])
			max_q_value = max(next_q_values)
			q_table[current_state, current_action] = (1 - alpha) * q_table[current_state, current_action] + alpha * (current_reward + gamma * max_q_value)
			loss = loss + (current_reward + gamma * max_q_value - q_table[current_state, current_action])**2
	loss_list.append(loss)
	episode = episode + 1

x = np.array(x)
x = x.reshape(x.shape[0], x.shape[1]*x.shape[2])
y = np.array(y)
states_1000 = np.array(list(states_1000))
states_1000 = states_1000.reshape(states_1000.shape[0], states_1000.shape[1]*states_1000.shape[2])

clf = MLPClassifier(hidden_layer_sizes=(10,10)) ## The loss function is cross entropy loss (log loss)
clf.fit(x, y)

# predicted = clf.predict(x)
# accuracy = metrics.accuracy_score(y, predicted)
# print(accuracy)
# for i in range(predicted.shape[0]):
# 	print(predicted[i])

prob_array = clf.predict_proba(states_1000)
entropy_array = []
for i in range(0, prob_array.shape[0]):
	entropy = 0
	for j in range(0, prob_array.shape[1]):
		entropy = entropy - prob_array[i][j] * log(prob_array[i][j])
	entropy_array.append(entropy)


state_al = states_1000[entropy_array.index(max(entropy_array))]
print(state_al)
for i in range(x.shape[0]):
	if list(x[i]) == list(state_al):
		print(y[i])
prob = prob_array[entropy_array.index(max(entropy_array))]
plt.bar(clf.classes_, prob)
plt.xlabel("Action")
plt.ylabel("Probability")
plt.show()


