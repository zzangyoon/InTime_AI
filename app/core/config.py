import torch
import os

dir_path = "app/data/member"
CLASS_LIST = os.listdir(dir_path)

NUM_CLASSES = len(CLASS_LIST)
MODEL_PATH = "app/models/first_Model.pth"
RECOGNITION_MODEL = "app/models/FRModel_20250918.pkl"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"