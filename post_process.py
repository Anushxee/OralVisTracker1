import os
import cv2
import numpy as np
from sklearn.cluster import KMeans

IMG_DIR = "dataset_split/test/images"        #path to test images
PRED_DIR = "runs/detect/predict2/labels"     #YOLO predicted labels (from save_txt=True)
OUT_DIR = "ordered_labels"                   #output folder for reordered labels
OUT_IMG_DIR = "ordered_images"               #output folder for annotated images


#Class ID -> FDI number
CLASS_TO_FDI = {
    0: 13, 1: 23, 2: 33, 3: 43, 4: 21, 5: 41, 6: 31, 7: 11,
    8: 16, 9: 26, 10: 36, 11: 46, 12: 14, 13: 34, 14: 44, 15: 24,
    16: 22, 17: 32, 18: 42, 19: 12, 20: 17, 21: 27, 22: 37, 23: 47,
    24: 15, 25: 25, 26: 35, 27: 45, 28: 18, 29: 28, 30: 38, 31: 48
}

#quadrant to color (BGR for OpenCV); fallback gray for unknown
QUAD_COLORS = {
    1: (0, 0, 255),   # Quadrant 1: upper right (red)
    2: (255, 0, 0),   # Quadrant 2: upper left (blue)
    3: (0, 255, 0),   # Quadrant 3: lower left (green)
    4: (0, 255, 255)  # Quadrant 4: lower right (yellow)
}

def get_quadrant_from_fdi(fdi):
    """Extracts the quadrant number (1-4) from FDI number."""
    return int(str(fdi)[0])

def post_process_and_draw(label_file, img_file, out_file, out_img_file):
    img = cv2.imread(img_file)
    if img is None:
        print(f"⚠️ Skipping {img_file}, could not load image.")
        return

    h, w, _ =img.shape
    teeth=[]

    #read yolo predictions
    with open(label_file, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) !=5:
                continue
            cls, cx, cy, bw, bh=map(float, parts)
            cls = int(cls)
            fdi_num = CLASS_TO_FDI.get(cls, -1)
            if fdi_num==-1:
                continue
            teeth.append({
                "cls":cls,
                "fdi_num":fdi_num,
                "cx":cx,
                "cy":cy,
                "bw":bw,
                "bh":bh,
            })

    if not teeth:
        print(f"⚠️ No teeth detected in {label_file}")
        return

    #Y-AXIS CLUSTERING FOR ARCH SPLIT 
    #cluster all teeth by normalized Y (vertical position) into 2 arches
    ys = np.array([[t["cy"]] for t in teeth])
    kmeans_y = KMeans(n_clusters=2, n_init=10, random_state=42).fit(ys)

    #get which cluster is upper/lower by comparing mean Y
    arch_labels= kmeans_y.labels_
    mean_cy=[np.mean([teeth[i]["cy"] for i in range(len(teeth)) if arch_labels[i]==cl]) for cl in [0,1]]
    upper_label=np.argmin(mean_cy)  
    lower_label=1 - upper_label

    #group by arch
    upper_teeth= [teeth[i] for i in range(len(teeth)) if arch_labels[i] == upper_label]
    lower_teeth= [teeth[i] for i in range(len(teeth)) if arch_labels[i] == lower_label]

    #X-MIDLINE SPLIT FOR LEFT/RIGHT IN EACH ARCH 
    def split_left_right(teeth_list):
        if not teeth_list:
            return [], []
        xs= np.array([[t["cx"]] for t in teeth_list])
        median_x= np.median(xs)
        left= [t for t in teeth_list if t["cx"] < median_x]
        right= [t for t in teeth_list if t["cx"] >= median_x]
        return left, right

    upper_left, upper_right= split_left_right(upper_teeth)
    lower_left, lower_right= split_left_right(lower_teeth)

    #SORT TEETH WITHIN QUADRANT(by X) 
    upper_left.sort(key=lambda t: t["cx"])
    upper_right.sort(key=lambda t: t["cx"])
    lower_left.sort(key=lambda t: t["cx"])
    lower_right.sort(key=lambda t: t["cx"])

    #DRAW AND SAVE LABELS 
    def draw_and_save(teeth_list, quadrant, color):
        final_labels = []
        for t in teeth_list:
            cx_pix, cy_pix, bw_pix, bh_pix = t["cx"] * w, t["cy"] * h, t["bw"] * w, t["bh"] * h
            x1, y1 = int(cx_pix - bw_pix/2), int(cy_pix - bh_pix/2)
            x2, y2 = int(cx_pix + bw_pix/2), int(cy_pix + bw_pix/2)
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
            cv2.putText(
                img, f"{t['fdi_num']} (Q{quadrant})", (x1, y1-5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2
            )
            final_labels.append(f"{t['cls']} {t['cx']:.6f} {t['cy']:.6f} {t['bw']:.6f} {t['bh']:.6f}")
        return final_labels

    final_labels=[]
    final_labels += draw_and_save(upper_right, 1, QUAD_COLORS[1])
    final_labels += draw_and_save(upper_left, 2, QUAD_COLORS[2])
    final_labels += draw_and_save(lower_left, 3, QUAD_COLORS[3])
    final_labels += draw_and_save(lower_right, 4, QUAD_COLORS[4])

    #save yolo-format labels
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, "w") as f:
        f.write("\n".join(final_labels))

    #save annotated image
    os.makedirs(OUT_IMG_DIR, exist_ok=True)
    cv2.imwrite(out_img_file, img)

    print(f"✅ Clustered & processed {os.path.basename(label_file)} → {out_file}, {out_img_file}")

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(OUT_IMG_DIR, exist_ok=True)

    for label_file in os.listdir(PRED_DIR):
        if not label_file.endswith(".txt"):
            continue
        img_file= os.path.join(IMG_DIR, label_file.replace(".txt", ".jpg"))
        label_path= os.path.join(PRED_DIR, label_file)
        out_path= os.path.join(OUT_DIR, label_file)
        out_img_path= os.path.join(OUT_IMG_DIR, label_file.replace(".txt", ".jpg"))

        if not os.path.exists(img_file):
            print(f"⚠️ No matching image for {label_file}, skipping.")
            continue

        post_process_and_draw(label_path, img_file, out_path, out_img_path)

if __name__ == "__main__":
    main()