import torch
import os

dir_path = "app/data/member"
class_list = os.listdir(dir_path)

NUM_CLASSES = len(class_list)
MODEL_PATH = "app/models/first_Model.pth"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"