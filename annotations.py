import os
import random
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image

image_root = "images"
annotation_root = "Annotations"

categories = ["Spurious_copper"]
category_short = {
    "Missing_hole": "MH",
    "Mouse_bite": "MB",
    "Open_circuit": "OC",
    "Short": "Sh",
    "Spur": "Sp",
    "Spurious_copper": "SC"
}

pairs = []
for cat in categories:
    img_dir = os.path.join(image_root, cat)
    ann_dir = os.path.join(annotation_root, cat)
    if not os.path.exists(img_dir) or not os.path.exists(ann_dir):
        continue
    for f in os.listdir(img_dir):
        if f.lower().endswith(".jpg"):
            name = os.path.splitext(f)[0]
            xml_path = os.path.join(ann_dir, name + ".xml")
            if os.path.exists(xml_path):
                pairs.append((os.path.join(img_dir, f), xml_path, cat))

samples = random.sample(pairs, min(5, len(pairs)))

def parse_xml(path):
    boxes = []
    labels = set()
    tree = ET.parse(path)
    root = tree.getroot()
    for obj in root.findall("object"):
        labels.add(obj.find("name").text)
        b = obj.find("bndbox")
        xmin = int(b.find("xmin").text)
        ymin = int(b.find("ymin").text)
        xmax = int(b.find("xmax").text)
        ymax = int(b.find("ymax").text)
        boxes.append((xmin, ymin, xmax, ymax))
    return boxes, labels

def expand(xmin, ymin, xmax, ymax, r=0.3):
    w = xmax - xmin
    h = ymax - ymin
    return (
        max(0, int(xmin - r * w)),
        max(0, int(ymin - r * h)),
        int(xmax + r * w),
        int(ymax + r * h)
    )

os.makedirs("annotated_outputs", exist_ok=True)

for i, (img_path, ann_path, cat) in enumerate(samples, 1):
    img = Image.open(img_path)
    boxes, labels = parse_xml(ann_path)

    print(f"\nImage: {img_path}")
    print(f"Defect class: {cat}")
    print(f"Short code: {category_short.get(cat, cat)}")
    print(f"XML labels: {', '.join(labels)}")
    print(f"Bounding boxes: {len(boxes)}")

    fig, ax = plt.subplots(figsize=(10, 6), dpi=1000)
    ax.imshow(img)
    ax.axis("off")

    for xmin, ymin, xmax, ymax in boxes:
        xmin, ymin, xmax, ymax = expand(xmin, ymin, xmax, ymax)
        ax.add_patch(
            patches.FancyBboxPatch(
                (xmin, ymin),
                xmax - xmin,
                ymax - ymin,
                linewidth=1.5,
                edgecolor="#f6ff00",
                facecolor="none",
                boxstyle="round",
                alpha=0.9
            )
        )
        ax.text(
            xmin - 80, ymin - 80,
            category_short.get(cat, cat),
            fontsize=18,
            fontname="Arial Rounded MT Bold",
            color="#f6ff00",
            weight="bold",
            bbox=dict(facecolor="black", alpha=0.5, boxstyle="round,pad=0.3")
        )

    out = os.path.join("annotated_outputs", f"annotated_{i}.png")
    plt.savefig(out, bbox_inches="tight", pad_inches=0.1, dpi=1000)
    plt.close(fig)

    print(f"Saved: {out}")

print("\nDone. Files in 'annotated_outputs/'")