import torch.nn as nn
import torch
from torchvision import models

from misc.layer import convDU, convLR

import torch.nn.functional as F
from misc.utils import *

import pdb

from efficientnet_pytorch import EfficientNet

# model_path = '../PyTorch_Pretrained/resnet101-5d3b4d8f.pth'



class EfficientNet_SFCN(nn.Module):
    def __init__(self, pretrained=True):
        super(EfficientNet_SFCN, self).__init__() 
        self.seen = 0
        
        self.res = EfficientNet.from_pretrained('efficientnet-b7') #perlu tambahin function from_pretrained?
        
        self.frontend = nn.Sequential(
            self.res._conv_stem, self.res._bn0, self.res._swish
        )

        self.convOut = nn.Sequential(nn.Conv2d(80, 64, kernel_size=1),nn.ReLU())
        self.convDU = convDU(in_out_channels=64,kernel_size=(1,9))
        self.convLR = convLR(in_out_channels=64,kernel_size=(9,1))

        # Final linear layer
        self.output_layer = nn.Sequential(nn.Conv2d(64, 1, kernel_size=1),nn.ReLU())

        # import IPython; IPython.embed()

    def forward(self,x):
        # x = self.res.extract_features(x)
        x = self.frontend(x)

        for idx in range(18):            
            drop_connect_rate = self.res._global_params.drop_connect_rate
            if drop_connect_rate:
                drop_connect_rate *= float(idx) / len(self.res._blocks) # scale drop connect_rate
            x = self.res._blocks[idx](x, drop_connect_rate=drop_connect_rate)

        # pdb.set_trace()
        # import IPython; IPython.embed()

        x = self.convOut(x)
        x = self.convDU(x)
        x = self.convLR(x)
        x = self.output_layer(x)

        x = F.upsample(x,scale_factor=8)
        return x    
