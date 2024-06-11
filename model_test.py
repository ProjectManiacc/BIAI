import math
import torch
from torchvision.transforms import functional as F
from PIL import Image, ImageDraw
from main import PetModel, MyDataset


def resize_image(image):
    width, height = image.size
    new_width = math.ceil(width / 32) * 32
    new_height = math.ceil(height / 32) * 32
    return image.resize((new_width, new_height))


# Load the model
model = torch.load('best_model_Normal.pth')
model.eval()

# Load and preprocess the image
image = Image.open('Images/AlbertPasek4.jpg')
# image = Image.open('test_no_animal.jpg')
image = resize_image(image)
image_tensor = F.to_tensor(image).unsqueeze(0)

image_pil = F.to_pil_image(image_tensor.squeeze(0))

# Create a draw object
draw = ImageDraw.Draw(image_pil)

with torch.no_grad():
    prediction = model(image_tensor)

# Print the prediction
print(prediction)

# Iterate over the detected objects
for box in prediction[0]:
    # The coordinates are in the format (xmin, ymin, xmax, ymax)
    draw.rectangle([(box[0], box[1]), (box[2], box[3])], outline="red", width=3)

# Display the image
image_pil.show()

# Pass the image through the model

label_mapping = {
    'NonMaskingBackground': 0,
    'MaskingBackground': 1,
    'Animal': 2,
    'NonMaskingForegroundAttention': 3
}

labels_of_interest = set(label_mapping.values())  # replace with the actual labels for your classes

# Check if an object of interest was detected
if any(label in labels_of_interest for label in prediction[0]):
    print("Object of interest detected!")
else:
    print("No object of interest detected.")

