import glob
import os.path as osp
import random
import numpy as np
import json
from PIL import Image
from tqdm import tqdm
import matplotlib.pyplot as plt

import torch
import torch.nn as nn
import torch.optim as optim
import torch.utils.data as data
import torchvision
from torchvision import models,transforms

torch.manual_seed(1234)
np.random.seed(1234)
random.seed(1234)

class ImageTransform():

    def __init__(self,resize,mean,std):
        self.data_transform = {
            "train":transforms.Compose([
                transforms.RandomResizedCrop(
                    resize,scale=(0.5,1.0)
                ),
                transforms.RandomHorizontalFlip(),
                transforms.ToTensor(),
                transforms.Normalize(mean,std)
            ]),
            "val":transforms.Compose([
                transforms.Resize(resize),
                transforms.CenterCrop(resize),
                transforms.ToTensor(),
                transforms.Normalize(mean,std)
            ])
        }

    def __call__(self,img,phase="train"):
        return self.data_transform[phase](img)

def make_datapath_list(phase="train"):
    rootpath = "./hymenoptera_data/"
    target_path = osp.join(rootpath+phase+"/**/*.jpg")
    print(target_path)

    path_list = []

    for path in glob.glob(target_path):
        path_list.append(path)

    return path_list

class HymenopteraDataset(data.Dataset):

    def __init__(self,file_list,transform = None,phase="train"):
        self.file_list = file_list
        self.transform = transform
        self.phase = phase

    def __len__(self):
        return len(self.file_list)

    def __getitem__(self,index):
        img_path = self.file_list[index]
        img = Image.open(img_path)

        img_transformed = self.transform(img,self.phase)

        if self.phase == "train":
            label = img_path[25:29]
        elif self.phase == "val":
            label = img_path[23:27]

        if label == "ants":
            label = 0
        if label == "bees":
            label = 1

        return img_transformed,label

def train_model(net,dataloaders_dict,criterion,optimizer,num_epochs):

    for epoch in range(num_epochs):
        print("Epoch{}/{}".format(epoch+1,num_epochs))
        print("--------------")

        for phase in ["train","val"]:
            if phase == "train":
                net.train()
            else:
                net.eval()

            epoch_loss = 0.0
            epoch_corrects = 0

            if (epoch == 0) and (phase == "train"):
                continue

            for inputs,labels in tqdm(dataloaders_dict[phase]):

                optimizer.zero_grad()

                with torch.set_grad_enabled(phase == "train"):
                    outputs = net(inputs)
                    loss = criterion(outputs,labels)
                    _,preds = torch.max(outputs,1)

                    if phase == "train":
                        loss.backward()
                        optimizer.step()

                    epoch_loss += loss.item() * inputs.size(0)

                    epoch_corrects += torch.sum(preds == labels.data)

            epoch_loss = epoch_loss / len(dataloaders_dict[phase].dataset)
            epoch_acc = epoch_corrects.double() / len(dataloaders_dict[phase].dataset)

            print("{} Loss:{:.4f} Acc:{:.4f}".format(phase,epoch_loss,epoch_acc))







