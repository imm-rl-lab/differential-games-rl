import torch
import torch.nn as nn

from models.double_naf import DoubleNAFAgent
from problems.point_on_a_plane.point_on_a_plane import PointOnAPlane
from utilities.DiffGamesResolver import DiffGamesResolver
from utilities.noises import OUNoise
from utilities.sequentialNetwork import Seq_Network

state_shape = 5
action_shape = 2
episode_n = 300


def init_u_agent(state_shape, action_shape, action_max, batch_size):
    mu_model = Seq_Network([state_shape, 50, 50, action_shape], nn.ReLU(), nn.Tanh())
    p_model = Seq_Network([state_shape, 50, 50, action_shape ** 2], nn.ReLU())
    v_model = Seq_Network([state_shape, 50, 50, 1], nn.ReLU())
    noise = OUNoise(2, threshold=action_max, threshold_min=0.001, threshold_decrease=0.003 * action_max)
    agent = DoubleNAFAgent(mu_model, p_model, v_model, noise, state_shape, action_shape, action_max, batch_size, gamma=0.9999)
    return agent


def init_v_agent(state_shape, action_shape, action_max, batch_size):
    mu_model = Seq_Network([state_shape, 50, 50, action_shape], nn.ReLU(), nn.Tanh())
    p_model = Seq_Network([state_shape, 50, 50, action_shape ** 2], nn.ReLU())
    v_model = Seq_Network([state_shape, 50, 50, 1], nn.ReLU())
    noise = OUNoise(2, threshold=action_max, threshold_min=0.001, threshold_decrease=0.003 * action_max)
    agent = DoubleNAFAgent(mu_model, p_model, v_model, noise, state_shape, action_shape, action_max, batch_size, gamma=0.9999)
    return agent


if __name__ == '__main__':
    env = PointOnAPlane()
    resolver = DiffGamesResolver()
    u_agent = init_u_agent(state_shape, action_shape, env.u_action_max, 128)
    v_agent = init_v_agent(state_shape, action_shape, env.v_action_max, 128)
    rewards = resolver.fit_agents(env, episode_n, u_agent, v_agent, fit_step=10)
    torch.save(u_agent.Q.state_dict(), './resultU')
    torch.save(v_agent.Q.state_dict(), './resultV')
