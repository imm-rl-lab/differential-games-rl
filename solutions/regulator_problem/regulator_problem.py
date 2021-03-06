import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn

from models.unlimited_naf import UnlimitedNAFAgent
from problems.regulator_problem.optimal_agent import OptimalAgent
from problems.regulator_problem.regulator_problem_env import RegulatorProblem
from utilities.noises import OUNoise
from utilities.sequentialNetwork import Seq_Network

env = RegulatorProblem()
state_shape = 5
action_shape = 1
episodes_n = 250

mu_model = Seq_Network([state_shape, 100, 100, 100, action_shape], nn.Sigmoid())
p_model = Seq_Network([state_shape, 100, 100, 100, action_shape ** 2], nn.Sigmoid())
v_model = Seq_Network([state_shape, 100, 100, 100, 1], nn.Sigmoid())
noise = OUNoise(action_shape, threshold=1, threshold_min=0.001, threshold_decrease=0.004)
batch_size = 200
agent = UnlimitedNAFAgent(mu_model, p_model, v_model, noise, state_shape, action_shape, batch_size, 1)


def play_and_learn(env):
    total_reward = 0
    state = env.reset()
    done = False
    step = 0
    while not done:
        action = agent.get_action(state)
        next_state, reward, done, _ = env.step(action)
        total_reward += reward
        done = step >= 100
        agent.fit(state, action, -reward, done, next_state)
        state = next_state
        step += 1
    t = env.t
    agent.noise.decrease()
    return total_reward, t


def agent_play(env, agent):
    state = env.reset()
    total_reward = 0
    ts = []
    us = []
    terminal_time = 5
    done = False
    step = 0
    while not done:
        action = agent.get_action(state)
        ts.append(env.t)
        next_state, reward, done, _ = env.step(action)
        total_reward += reward
        us.append(action[0])
        state = next_state
        done = env.t >= terminal_time
        step += 1
    plt.plot(ts, us)
    return total_reward


rewards = np.zeros(episodes_n)
mean_rewards = np.zeros(episodes_n)
times = np.zeros(episodes_n)
mean_times = np.zeros(episodes_n)
for episode in range(episodes_n):
    reward, t = play_and_learn(env)
    rewards[episode] = reward
    times[episode] = t
    mean_reward = np.mean(rewards[max(0, episode - 50):episode + 1])
    mean_time = np.mean(times[max(0, episode - 50):episode + 1])
    mean_rewards[episode] = mean_reward
    mean_times[episode] = mean_time
    print("episode=%.0f, noise_threshold=%.3f, total reward=%.3f, mean reward=%.3f, t=%.3f" % (
        episode, agent.noise.threshold, rewards[episode], mean_reward, mean_time))

agent.noise.threshold = 0
reward = agent_play(env, agent)
optimal_reward = agent_play(env, OptimalAgent())
plt.title('track')
plt.legend(['NAF', 'Optimal'])
plt.show()
print('optimal', optimal_reward)
print('fitted', reward)
plt.plot(range(episodes_n), mean_rewards)
plt.plot(range(episodes_n), optimal_reward * np.ones(episodes_n))
plt.title('fit')
plt.legend(['NAF', 'Optimal'])
plt.show()
plt.plot(range(episodes_n), mean_times)
plt.title('times')
plt.legend(['NAF'])
plt.show()
torch.save(agent.Q.state_dict(), './result')
