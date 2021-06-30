from functools import partial

import torch
import torch.nn as nn
import torch.nn.functional as F


class DINOLoss(nn.Module):

    def __init__(self, weights_momentum, center_momentum, temperature):
        super(DINOLoss, self).__init__()
        self.weights_momentum = weights_momentum
        self.center_momentum = center_momentum
        self.temperature = temperature
        self.softmax = partial(F.softmax, dim=1)
        self.center = torch.empty()
        self.loss = nn.CrossEntropyLoss()

    def forward(self, student_output, teacher_output):
        s1, s2 = student_output
        t1, t2 = teacher_output
        s1, s2 = self.softmax(s1 / self.temperature), self.softmax(s2 / self.temperature)
        t1, t2 = self.softmax((t1.detach() - self.center) / self.temperature), \
            self.softmax((t2.detach() - self.center) / self.temperature)
        self.center = self.center * self.center_momentum + (
                1 - self.center_momentum) * torch.cat([t1, t2], dim=0).mean(dim=0)
        return 0.5 * (self.loss(t1, s2) + self.loss(t2, s1))
