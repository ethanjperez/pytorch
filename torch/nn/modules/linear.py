import math

import torch
from torch.nn.parameter import Parameter
from .. import functional as F
from .module import Module


class Linear(Module):
    r"""Applies a linear transformation to the incoming data: :math:`y = Ax + b`

    Args:
        in_features: size of each input sample
        out_features: size of each output sample
        bias: If set to False, the layer will not learn an additive bias.
            Default: ``True``

    Shape:
        - Input: :math:`(N, *, in\_features)` where :math:`*` means any number of
          additional dimensions
        - Output: :math:`(N, *, out\_features)` where all but the last dimension
          are the same shape as the input.

    Attributes:
        weight: the learnable weights of the module of shape
            `(out_features x in_features)`
        bias:   the learnable bias of the module of shape `(out_features)`

    Examples::

        >>> m = nn.Linear(20, 30)
        >>> input = torch.randn(128, 20)
        >>> output = m(input)
        >>> print(output.size())
    """

    def __init__(self, in_features, out_features, bias=True):
        super(Linear, self).__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.weight = Parameter(torch.Tensor(out_features, in_features))
        if bias:
            self.bias = Parameter(torch.Tensor(out_features))
        else:
            self.register_parameter('bias', None)
        self.reset_parameters()

    def reset_parameters(self):
        stdv = 1. / math.sqrt(self.weight.size(1))
        self.weight.data.uniform_(-stdv, stdv)
        if self.bias is not None:
            self.bias.data.uniform_(-stdv, stdv)

    def forward(self, input):
        return F.linear(input, self.weight, self.bias)

    def extra_repr(self):
        return 'in_features={}, out_features={}, bias={}'.format(
            self.in_features, self.out_features, self.bias is not None
        )


class Bilinear(Module):
    r"""Applies a bilinear transformation to the incoming data:
    :math:`y = x_1 A x_2 + b`

    Args:
        in1_features: size of each first input sample
        in2_features: size of each second input sample
        out_features: size of each output sample
        bias: If set to False, the layer will not learn an additive bias.
            Default: ``True``

    Shape:
        - Input: :math:`(N, *, \text{in1_features})`, :math:`(N, *, \text{in2_features})`
          where :math:`*` means any number of additional dimensions. All but the last
          dimension of the inputs should be the same.
        - Output: :math:`(N, *, \text{out_features})` where all but the last dimension
          are the same shape as the input.

    Attributes:
        weight: the learnable weights of the module of shape
            `(out_features x in1_features x in2_features)`
        bias:   the learnable bias of the module of shape `(out_features)`

    Examples::

        >>> m = nn.Bilinear(20, 30, 40)
        >>> input1 = torch.randn(128, 20)
        >>> input2 = torch.randn(128, 30)
        >>> output = m(input1, input2)
        >>> print(output.size())
    """

    def __init__(self, in1_features, in2_features, out_features, bias=True):
        super(Bilinear, self).__init__()
        self.in1_features = in1_features
        self.in2_features = in2_features
        self.out_features = out_features
        self.weight = Parameter(torch.Tensor(out_features, in1_features, in2_features))

        if bias:
            self.bias = Parameter(torch.Tensor(out_features))
        else:
            self.register_parameter('bias', None)
        self.reset_parameters()

    def reset_parameters(self):
        stdv = 1. / math.sqrt(self.weight.size(1))
        self.weight.data.uniform_(-stdv, stdv)
        if self.bias is not None:
            self.bias.data.uniform_(-stdv, stdv)

    def forward(self, input1, input2):
        return F.bilinear(input1, input2, self.weight, self.bias)

    def extra_repr(self):
        return 'in1_features={}, in2_features={}, out_features={}, bias={}'.format(
            self.in1_features, self.in2_features, self.out_features, self.bias is not None
        )


class FiLM(Module):
    r"""Applies Feature-wise Linear Modulation to the incoming data as described in
    the paper `FiLM: Visual Reasoning with a General Conditioning Layer`_ .
    
    .. math::
        y_{n,c,*} = \gamma_{n,c} * x_{n,c,*} + \beta_{n,c},

    where :math:`\gamma_{n,c}` and :math:`\beta_{n,c}` are scalars and operations are
    broadcast over any additional dimensions of :math:`x`

    Shape:
        - Input: :math:`(N, C, *)` where :math:`*` means any number of additional
          dimensions
        - Gamma: :math:`(N, C)`
        - Beta: :math:`(N, C)`
        - Output: :math:`(N, C, *)`, same shape as the input

    Examples::

        >>> m = nn.FiLM()
        >>> input = torch.randn(128, 20, 4, 4)
        >>> gammas = torch.randn(128, 20)
        >>> betas = torch.randn(128, 20)
        >>> m(input, gammas, betas)
        >>> print(output.size())
        
    .. _`FiLM: Visual Reasoning with a General Conditioning Layer`:
        https://arxiv.org/abs/1709.07871
    """
    
    def forward(self, input, gammas, betas):
        for _ in range(input.dim() - 2):
            gammas = gammas.unsqueeze(-1)
            betas = betas.unsqueeze(-1)
        return gammas * input + betas
    
    
# TODO: PartialLinear - maybe in sparse?
