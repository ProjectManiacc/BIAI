#!/usr/bin/python3
import os
import pathlib
import json
import cv2
import numpy as np

input_dir = "./zdjecia"
output_dir = "./wynik"

CATEGORY_COLORS = {
    1: (0, 0, 255),     # NonMaskingBackground
    2: (0, 255, 0),     # MaskingBackground
    3: (255, 0, 0),     # Animal
    4: (255, 255, 255),  # NonMaskingForegroundAttention
}

written_paths = {}


def get_coco_paths():
    coco_paths = []
    for path in os.listdir(input_dir):
        full_path = os.path.join(input_dir, path)
        if os.path.isfile(full_path) and pathlib.Path(full_path).suffix == ".json":
            if "coco" in full_path.lower():
                coco_paths.append(full_path)

    print(f"Found {len(coco_paths)} COCO files...")
    return coco_paths


def load_cocos(coco_paths):
    cocos = []
    for coco_path in coco_paths:
        with open(coco_path, "r") as f:
            coco = json.load(f)
            coco["path"] = coco_path
            cocos.append(coco)
    print(f"Loaded {len(cocos)} COCO files...")
    return cocos


def process_cocos(cocos):
    broken_cocos = 0
    failed_cocos = 0
    failed_images = 0
    total_images = 0
    for coco in cocos:
        try:
            valid_coco = True
            for image_info in coco['images']:
                total_images = total_images + 1
                image_path = os.path.join(input_dir, image_info['file_name'])
                image = None
                try:
                    image = cv2.imdecode(np.fromfile(
                        image_path, dtype=np.uint8), -1)
                except KeyboardInterrupt:
                    pass
                except:
                    print(f"Failed to load '{image_path}' - skipping...")
                    failed_images = failed_images + 1
                    valid_coco = False
                else:
                    # print(f"Processing {image_path}...")
                    process_coco_img(coco, image_info, image)
            if not valid_coco:
                broken_cocos = broken_cocos + 1
        except KeyError:
            print(f"Some moron doesn't know what COCO is - {coco['path']}")
            failed_cocos = failed_cocos + 1
    total_cocos = len(cocos)
    valid_cocos = total_cocos - failed_cocos - broken_cocos
    print(f"Loaded {total_images - failed_images}/{total_images} images.")
    print(f"{valid_cocos}/{total_cocos} COCOs valid ({failed_cocos} are utter crap, {broken_cocos} refernce bad images)")


def to_points(l):
    return [l[i:i+2] for i in range(0, len(l), 2)]


def process_coco_img(coco, image_info, image):
    output_path = os.path.join(output_dir, image_info['file_name'] + ".png")
    mask_data = np.zeros((image.shape[0],image.shape[1],3), dtype=np.uint8)

    valid_segments = 0
    for anno in coco['annotations']:
        image_id = int(anno['image_id'])
        category_id = int(anno['category_id'])
        if image_id != image_info['id']:
            continue
        if category_id not in CATEGORY_COLORS:
            print(
                f"Category ID {anno['category_id']} in {coco['path']} is not known - skipping annotation!")
            continue
        color = CATEGORY_COLORS[category_id]

        def process_segment(segment):
            nonlocal valid_segments, mask_data, color, anno
            valid_segments = valid_segments + 1
            points = to_points(segment)
            point_data = np.array(points, dtype=np.int32)
            # print(point_data)
            try:
                cv2.fillPoly(mask_data,  np.array([point_data]), color)
            except KeyboardInterrupt:
                pass
            except:
                print(f"Failed filling polygon - annotation ID {anno['id']}")
                pass

        # Thank you, Michalik.Tomasz, for making me write this cursed code
        if hasattr(anno['segmentation'][0], "__len__"):
            for segment in anno['segmentation']:
                process_segment(segment)
        else:
            process_segment(anno['segmentation'])

    if valid_segments == 0:
        print(f"{image_info['file_name']} doesn't have any valid annotations!")

    try:
        # print(f"Writing {output_path}...")
        if output_path in written_paths:
            previous = written_paths[output_path]
            print(
                f"Warning: {output_path} has already been written this time! (ref. by {previous['coco_path']}, now reading {coco['path']})")
        else:
            written_paths[output_path] = {'coco_path': coco['path']}
        success = cv2.imwrite(output_path, mask_data)

        if not success:
            print(
                f"Warning: OpenCV imwrite() probably errored on {output_path}")
    except KeyboardInterrupt:
        pass
    except:
        print(f"OpenCV error when writing {output_path}")


if not os.path.exists(output_dir):
    try:
        os.mkdir(output_dir)
    except:
        print(f"Failed to create output dir {output_dir}")
        exit(1)

process_cocos(load_cocos(get_coco_paths()))
print(f"Written {len(written_paths)} unique image paths.")