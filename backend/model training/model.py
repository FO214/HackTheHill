from ultralytics import YOLO

# Load a pretrained YOLOv8 model
model = YOLO('../yolov8n.pt')  # You can change 'yolov8n.pt' to a larger model if necessary

# Train the model on your black dot dataset
model.train(
    data='/path/to/data.yaml',  # Path to the data.yaml file
    epochs=50,                  # Number of training epochs
    imgsz=640,                  # Image size for training
    batch=16,                   # Batch size for training
    name='black_dot_tracker'     # Name of the training run
)
