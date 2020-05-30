import torch
from torch import nn


class Seq_Network(nn.Module):
    def __init__(self, layers, hidden_activation, output_activation=None, batch_norm=True):
        super().__init__()
        hidden_layers = layers[:-1]
        network = [nn.Sequential(nn.Linear(i, o), hidden_activation, nn.BatchNorm1d(o)) for i, o in
                   zip(hidden_layers, hidden_layers[1:])]
        network.append(nn.Linear(layers[-2], layers[-1]))
        if output_activation:
            network.append(output_activation)
        self.network = nn.Sequential(*network)
        self.apply(self._init_weights_)

    def forward(self, tensor):
        self.network.train()
        return self.network(tensor)

    def inference(self, tensor):
        self.network.eval()
        return self.network(tensor.unsqueeze(0))[0]

    def _init_weights_(self, m):
        if type(m) == nn.Linear:
            torch.nn.init.xavier_normal_(m.weight)
            m.bias.data.fill_(0.01)
