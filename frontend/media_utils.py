import os
import glob
import cv2
from config import ANNOTATED_DIR

DEFAULT_ANNOTATED_DIR = ANNOTATED_DIR

def get_latest_frame(folder=DEFAULT_ANNOTATED_DIR):
    if not os.path.exists(folder):
        return None
    list_of_files = glob.glob(f"{folder}/*.[jJ][pP][gG]") + glob.glob(f"{folder}/*.[pP][nN][gG]")
    if not list_of_files:
        return None
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file

def generate_timelapse(input_folder=DEFAULT_ANNOTATED_DIR, output_file="temp_timelapse.webm", fps=5):
   
    images = sorted(glob.glob(f"{input_folder}/*.[jJ][pP][gG]") + glob.glob(f"{input_folder}/*.[pP][nN][gG]"))
    
    if not images:
        return False
        
    frame = cv2.imread(images[0])
    if frame is None:
        return False
        
    height, width, layers = frame.shape
    
   
    fourcc = cv2.VideoWriter_fourcc(*'VP80')
    video = cv2.VideoWriter(output_file, fourcc, fps, (width, height))
    
   
    if not video.isOpened():
        return False
    
   
    for image_path in images[-100:]: 
        img = cv2.imread(image_path)
        if img is not None:
            video.write(img)
        
    video.release()
    return True