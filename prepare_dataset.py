import os
import shutil
import splitfolders

IMAGES_DIR = "images"   
LABELS_DIR = "labels"   
OUTPUT_DIR = "dataset"  #final split dataset
YAML_FILE = "data.yaml" 

images = {os.path.splitext(f)[0] for f in os.listdir(IMAGES_DIR) if f.lower().endswith(('.jpg', '.png'))}
labels = {os.path.splitext(f)[0] for f in os.listdir(LABELS_DIR) if f.lower().endswith('.txt')}

extra_images = images - labels
extra_labels = labels - images

if extra_images:
    print(f"⚠️ Extra images without labels: {extra_images}")
    for e in extra_images:
        os.remove(os.path.join(IMAGES_DIR, e + ".jpg"))

if extra_labels:
    print(f"⚠️ Extra labels without images: {extra_labels}")
    for e in extra_labels:
        os.remove(os.path.join(LABELS_DIR, e + ".txt"))

print("✅ Image–Label pairs are now clean and matched.")

#dataset folder in yolo format
if os.path.exists(OUTPUT_DIR):
    shutil.rmtree(OUTPUT_DIR)

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "images"))
os.makedirs(os.path.join(OUTPUT_DIR, "labels"))

shutil.copytree(IMAGES_DIR, os.path.join(OUTPUT_DIR, "images"), dirs_exist_ok=True)
shutil.copytree(LABELS_DIR, os.path.join(OUTPUT_DIR, "labels"), dirs_exist_ok=True)

splitfolders.ratio(OUTPUT_DIR, output=OUTPUT_DIR + "_split", seed=42, ratio=(.8, .1, .1))

print("✅ Dataset split into train/val/test.")


yaml_content = """train: dataset_split/train/images
val: dataset_split/val/images
test: dataset_split/test/images

names:
  0: Canine (13)
  1: Canine (23)
  2: Canine (33)
  3: Canine (43)
  4: Central Incisor (21)
  5: Central Incisor (41)
  6: Central Incisor (31)
  7: Central Incisor (11)
  8: First Molar (16)
  9: First Molar (26)
  10: First Molar (36)
  11: First Molar (46)
  12: First Premolar (14)
  13: First Premolar (34)
  14: First Premolar (44)
  15: First Premolar (24)
  16: Lateral Incisor (22)
  17: Lateral Incisor (32)
  18: Lateral Incisor (42)
  19: Lateral Incisor (12)
  20: Second Molar (17)
  21: Second Molar (27)
  22: Second Molar (37)
  23: Second Molar (47)
  24: Second Premolar (15)
  25: Second Premolar (25)
  26: Second Premolar (35)
  27: Second Premolar (45)
  28: Third Molar (18)
  29: Third Molar (28)
  30: Third Molar (38)
  31: Third Molar (48)
"""

with open(YAML_FILE, "w") as f:
    f.write(yaml_content)

print(f"✅ {YAML_FILE} created successfully!")
