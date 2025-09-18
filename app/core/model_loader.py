from app.core.config import NUM_CLASSES, MODEL_PATH, DEVICE
from torchvision import models
import torch

model = models.resnet34()
model.fc = torch.nn.Linear(model.fc.in_features, NUM_CLASSES)
model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
model.eval().to(DEVICE)