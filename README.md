🦷OralVisTracker
 
➡Tooth detection & numbering system using YOLOv8 on dental X-ray images.

✅Setup
➡️Clone repo and move into it:

     git clone https://github.com/Anushxee/OralVisTracker.git
     cd OralVisTracker
➡️Create & activate virtual environment:

     python -m venv venv
     # On Windows (PowerShell)
     .\venv\Scripts\activate
     # On Linux/Mac
     source venv/bin/activate
➡️Install dependencies: opencv-contrib-python, ultralytics, PyTorch, numpy, matplotlib, sk-learn
     
     pip install opencv-contrib-python ultralytics torch torchvision torchaudio numpy matplotlib scikit-learn

✅Dataset
➡️Dataset structure should look like:

dataset_split/
├── train/
│   ├── images/
│   └── labels/
├── val/
│   ├── images/
│   └── labels/
├── test/
│   ├── images/
│   └── labels/

✅Training
➡️Model used: yolov8

       yolo detect train data=data.yaml model=yolov8s.pt epochs=30 imgsz=640

➡data.yaml should point to your dataset paths.
➡model=yolov8s.pt loads pretrained YOLOv8 small.
➡epochs can be adjusted based on computing power/time restraints.

➡️Run predictions on test set:
          
          yolo detect predict model=runs/detect/train/weights/best.pt source=dataset_split/test/images save=True save_txt=True

➡Results will be saved in runs/detect/predict/

✅Post-Processing
➡To reorder detected teeth into proper FDI numbering and separate quadrants
➡Reordered labels will be saved in: ordered_labels/
➡Reordered images will be saved in: ordered_images/




