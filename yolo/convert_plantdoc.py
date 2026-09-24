import json
import os
import shutil

BASE = os.path.expanduser("~/agri_rover_ws/yolo")

DATASET = os.path.join(BASE, "plant_dataset")
SOURCE_IMAGES = os.path.join(
    BASE, "plant_doc_detection", "plant_diseases", "images"
)
ANNOTATIONS = os.path.join(
    BASE, "plant_doc_detection", "annotations"
)

# PlantDoc categories mapped to our two project classes
HEALTHY = {
    "apple_leaf",
    "bell_pepper_leaf",
    "blueberry_leaf",
    "cherry_leaf",
    "peach_leaf",
    "potato_leaf",
    "raspberry_leaf",
    "soyabean_leaf",
    "strawberry_leaf",
    "tomato_leaf",
    "grape_leaf",
}

DISEASED = {
    "apple_scab_leaf",
    "apple_rust_leaf",
    "bell_pepper_leaf_spot",
    "corn_gray_leaf_spot",
    "corn_leaf_blight",
    "corn_rust_leaf",
    "potato_leaf_early_blight",
    "potato_leaf_late_blight",
    "squash_powdery_mildew_leaf",
    "tomato_early_blight_leaf",
    "tomato_septoria_leaf_spot",
    "tomato_leaf_bacterial_spot",
    "tomato_leaf_late_blight",
    "tomato_leaf_mosaic_virus",
    "tomato_leaf_yellow_virus",
    "tomato_mold_leaf",
    "tomato_two_spotted_spider_mites_leaf",
    "grape_leaf_black_rot",
}


def convert_split(split):
    json_file = os.path.join(
        ANNOTATIONS,
        f"plant_diseases_instances_{split}.json"
    )

    image_dir = os.path.join(
        DATASET, "images", split
    )

    label_dir = os.path.join(
        DATASET, "labels", split
    )

    os.makedirs(image_dir, exist_ok=True)
    os.makedirs(label_dir, exist_ok=True)

    with open(json_file, "r") as f:
        data = json.load(f)

    categories = {
        category["id"]: category["name"]
        for category in data["categories"]
    }

    images = {
        image["id"]: image
        for image in data["images"]
    }

    annotations_by_image = {}

    for annotation in data["annotations"]:
        image_id = annotation["image_id"]

        if image_id not in annotations_by_image:
            annotations_by_image[image_id] = []

        annotations_by_image[image_id].append(annotation)

    copied = 0
    labeled = 0
    skipped = 0

    for image_id, image in images.items():

        filename = os.path.basename(image["file_name"])

        source = os.path.join(
            SOURCE_IMAGES,
            filename
        )

        if not os.path.exists(source):
            print(f"Missing image: {filename}")
            skipped += 1
            continue

        destination = os.path.join(
            image_dir,
            filename
        )

        shutil.copy2(source, destination)
        copied += 1

        label_file = os.path.splitext(filename)[0] + ".txt"

        label_path = os.path.join(
            label_dir,
            label_file
        )

        lines = []

        for annotation in annotations_by_image.get(image_id, []):

            category_name = categories.get(
                annotation["category_id"]
            )

            if category_name in HEALTHY:
                class_id = 0

            elif category_name in DISEASED:
                class_id = 1

            else:
                continue

            x, y, width, height = annotation["bbox"]

            image_width = image["width"]
            image_height = image["height"]

            # COCO -> YOLO normalized coordinates
            center_x = (x + width / 2) / image_width
            center_y = (y + height / 2) / image_height

            norm_width = width / image_width
            norm_height = height / image_height

            lines.append(
                f"{class_id} "
                f"{center_x:.6f} "
                f"{center_y:.6f} "
                f"{norm_width:.6f} "
                f"{norm_height:.6f}"
            )

        if lines:
            with open(label_path, "w") as f:
                f.write("\n".join(lines) + "\n")

            labeled += 1

    print(f"\n{split.upper()} SET")
    print(f"Images copied: {copied}")
    print(f"Images labeled: {labeled}")
    print(f"Images skipped: {skipped}")


print("Starting PlantDoc → YOLO conversion...\n")

convert_split("train")
convert_split("val")

print("\nConversion complete.")
