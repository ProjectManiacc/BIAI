from PIL import Image

# Load the image
im = Image.open("Masks/Dusza.Jakub.1.png")

# Get the pixel data
pixel_data = im.load()

# Set up initial values for the most left, right, up, and down coordinates
leftmost = im.width
rightmost = 0
topmost = im.height
bottommost = 0

# Find the most left, right, up, and down coordinates of blue pixels
for x in range(im.width):
    for y in range(im.height):
        if pixel_data[x, y] == (0, 0, 255):  # Blue pixels have RGB values of (0, 0, 255)
            if x < leftmost:
                leftmost = x
            if x > rightmost:
                rightmost = x
            if y < topmost:
                topmost = y
            if y > bottommost:
                bottommost = y

# Calculate the width and height of the cropped image
width = rightmost - leftmost
height = bottommost - topmost

# Determine the scaling factor to resize the cropped image to 450x450
scale = max(width, height) / 450.0

# Calculate the x and y offsets for the cropped image
x_offset = leftmost + int(width / 2) - int(225 * scale)
y_offset = topmost + int(height / 2) - int(225 * scale)

# Calculate the boundaries of the cropping rectangle
left = max(leftmost - 10, 0)
top = max(topmost - 10, 0)
right = min(rightmost + 10, im.width)
bottom = min(bottommost + 10, im.height)

# Create a new cropped image with a normal offset and scaled to 450x450
cropped_im = im.crop((left, top, right, bottom))
cropped_im = cropped_im.resize((int(width / scale), int(height / scale)))

# Create a new blank image with a size of 450x450 and paste the cropped image onto it
output_im = Image.new("RGB", (450, 450), color=(255, 255, 255))
output_im.paste(cropped_im, (-x_offset, -y_offset))

# Copy the original pixels from the input image to the output image
output_data = output_im.load()
for x in range(output_im.width):
    for y in range(output_im.height):
        if (x < -x_offset or x >= -x_offset + cropped_im.width or
                y < -y_offset or y >= -y_offset + cropped_im.height):
            if (x + x_offset >= 0 and x + x_offset < im.width and
                    y + y_offset >= 0 and y + y_offset < im.height):
                output_data[x, y] = pixel_data[x + x_offset, y + y_offset]

# Save the output image
output_im.save("output_image.png")
