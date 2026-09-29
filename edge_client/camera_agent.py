import time
import requests
import os
import glob
import logging
import cv2 
from ultralytics import YOLO

logging.basicConfig(level=logging.INFO, format='%(message)s')

API_URL = "http://localhost:8000/telemetry/"
FRAMES_DIR = "demo_frames"
ANNOTATED_DIR = "annotated_frames"
MODEL_PATH = "best.pt" 

CLASS_MAPPING = {
    "samosval": "dump_truck",
    "truck": "dump_truck",
    "excavator": "excavator",
    "ekskavator": "excavator",
    "Самосвал": "dump_truck",
    "Экскаватор": "excavator"
}

def get_active_stage_id():
    api_project_url = "http://localhost:8000/projects/1"
    try:
        response = requests.get(api_project_url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            for stage in data.get("stages", []):
                if stage.get("nlp_stage_id") == "STAGE_EARTH_WORK":
                    stage_id = stage["id"]
                    logging.info(f"🎯 Этап найден! Название: '{stage['name']}', ID: {stage_id}")
                    return stage_id
            logging.warning("⚠️ Этап с тегом STAGE_EARTH_WORK не найден в базе!")
    except Exception as e:
        logging.error(f"❌ Ошибка связи с бэкендом: {e}")
    return 1

def run_demo():
    
    if not os.path.exists(MODEL_PATH):
        logging.error(f"Файл модели {MODEL_PATH} не найден!")
        return
        
   
    os.makedirs(ANNOTATED_DIR, exist_ok=True)
        
    logging.info(f"Загрузка модели YOLO из {MODEL_PATH}...")
    model = YOLO(MODEL_PATH)
    
   
    frame_paths = sorted(glob.glob(os.path.join(FRAMES_DIR, "*.png")) + glob.glob(os.path.join(FRAMES_DIR, "*.jpg")))
    
    if not frame_paths:
        logging.error(f"Кадры не найдены в папке {FRAMES_DIR}!")
        return

    logging.info(f"Найдено {len(frame_paths)} кадров. Запуск AI инференса и рендера рамок...")
    
    while True:
        stage_id = get_active_stage_id()
        for path in frame_paths:
            filename = os.path.basename(path)
            
            results = model(path, verbose=False)
            
           
           
            annotated_frame = results[0].plot() 
           
            save_path = os.path.join(ANNOTATED_DIR, filename)
            cv2.imwrite(save_path, annotated_frame)
           
            
            detected_objects = []
            
            for box in results[0].boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                original_class_name = results[0].names[cls_id]
                mapped_class_name = CLASS_MAPPING.get(original_class_name, original_class_name)
                
                if conf > 0.5:
                    detected_objects.append({
                        "class": mapped_class_name,
                        "conf": round(conf, 2)
                    })
            
            log_objs = ", ".join([f"{o['class']} ({o['conf']})" for o in detected_objects])
            logging.info(f"[Кадр {filename}] Найдено: {log_objs if log_objs else 'Ничего'}")
            
            payload = {
                "stage_id": stage_id,
                "detected_objects": detected_objects,
                "calculated_volume": 0.0 
            }
            
            try:
                response = requests.post(API_URL, json=payload, timeout=5)
                if response.status_code != 200:
                    logging.error(f"❌ Ошибка сервера: {response.text}")
            except requests.exceptions.ConnectionError:
                logging.error("Сервер недоступен.")
            
            time.sleep(2)
            
        logging.info("Все кадры обработаны. Повтор через 10 секунд...")
        time.sleep(10)

if __name__ == "__main__":
    run_demo()