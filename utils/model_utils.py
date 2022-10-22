from typing import List

import torch
from torchvision import models
from torchvision.transforms import Compose, Resize, ToTensor, Normalize


class Identity(torch.nn.Module):
    """
    Model that does identity mapping.
    Used to remove last fully connected layer from torch model.
    """

    def __init__(self):
        super(Identity, self).__init__()

    def forward(self, x):
        return x


def resnet18_model_creator():
    '''
    Returns:
        Pytorch's resnet50 ImageNet pretrained model
    '''
    model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    model.fc = Identity()  # Remove the prediction head
    model.eval()
    model = torch.jit.script(model)
    return model


def resnet_transform(size: int = 224,
                     mean: List = [0.485, 0.456, 0.406],
                     std: List = [0.229, 0.224, 0.225]):
    '''
    Creates image pre-processing transformer for model.

    Args:
        size (int): height and width size for transformed image.
        mean (List): mean values for 3 channels
        std (List): std values for 3 channels

    Returns:
        (torchvision.transforms): transformer object
    '''
    return Compose([
        Resize(size),
        ToTensor(),
        Normalize(mean=mean,
                  std=std),
    ])
