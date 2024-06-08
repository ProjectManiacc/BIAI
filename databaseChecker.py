from PIL import Image
import os


# Set the input and output directories
def resizeDatabase():
    input_image_dir = "Images"
    input_mask_dir = "Masks"
    try:
        os.makedirs("DataBaseImages", exist_ok=True)
        print("Directory '%s' created successfully" % "DataBaseImages")
    except OSError as error:
        print("Directory '%s' can not be created" % "DataBaseImages")

    try:
        os.makedirs("DataBaseMasks", exist_ok=True)
        print("Directory '%s' created successfully" % "DataBaseMasks")
    except OSError as error:
        print("Directory '%s' can not be created" % "DataBaseMasks")

    output_image_dir = "DataBaseImages"
    output_mask_dir = "DataBaseMasks"

    # Iterate over all files in the input image directory
    for filename in os.listdir(input_image_dir):
        # Check if the file is an image
        if filename.endswith((".jpg", ".jpeg", ".JPG", ".png")):
            # Open the image file
            input_path = os.path.join(input_image_dir, filename)
            output_path = os.path.join(output_image_dir, filename)
            # Check if the output file already exists
            if os.path.exists(output_path):
                print(f"Skipping {filename} - output file already exists")
                continue
            # Open the image file
            image = Image.open(input_path)

            # Resize the image to 480x480
            resized_image = image.resize((480, 480))

            # Save the resized image to the output directory with the original filename and extension
            resized_image.save(output_path)

    # Iterate over all files in the input mask directory
    for filename in os.listdir(input_mask_dir):
        # Check if the file is a mask
        if filename.endswith(".png"):
            # Open the mask file
            input_path = os.path.join(input_mask_dir, filename)
            output_path = os.path.join(output_mask_dir, filename)
            # Check if the output file already exists
            if os.path.exists(output_path):
                print(f"Skipping {filename} - output file already exists")
                continue
            # Open the mask file
            mask = Image.open(input_path)

            # Resize the mask to 480x480
            resized_mask = mask.resize((480, 480))

            # Save the resized mask to the output directory with the original filename and extension
            resized_mask.save(output_path)


def check_image_mask_alignment(img_dir, mask_dir):
    img_files = os.listdir(img_dir)
    mask_files = os.listdir(mask_dir)

    img_names = set([os.path.splitext(file)[0] for file in img_files])
    mask_names = set([os.path.splitext(file)[0] for file in mask_files])

    common_files = img_names.intersection(mask_names)
    not_aligned = sorted(list(img_names.symmetric_difference(mask_names)))

    return not_aligned, len(common_files), len(img_files), len(mask_files)


def main():
    img_dir = "DataBaseImages"
    mask_dir = "DataBaseMasks"

    resizeDatabase()

    not_aligned_files, num_common_files, num_images, num_masks = check_image_mask_alignment(img_dir, mask_dir)
    if not_aligned_files:
        print("Images and masks are not aligned for the following files:")
        print(not_aligned_files)
    else:
        print("Images and masks are aligned.")

    print("Number of common files (aligned files):", num_common_files)
    print("Number of images:", num_images)
    print("Number of masks:", num_masks)


if __name__ == "__main__":
    main()
