import time
import requests
import random
import logging

logging.basicConfig(level=logging.INFO)


API_URL = "http://localhost:8000/telemetry/"
CAMERA_ID = "cam_01_pit"



ACTIVE_STAGE_ID = 1 

def capture_frame():
    return "dummy_frame_data"

def run_cv_inference(frame):
    
    objects = []
    
    
    if random.random() > 0.3:
        objects.append({"class": "dump_truck", "conf": 0.92, "bbox": [10, 20, 100, 200]})
        
    
    if random.random() > 0.5:
        objects.append({"class": "excavator", "conf": 0.88, "bbox": [300, 150, 400, 350]})
        
    return objects

def main_loop():
    logging.info(f"Запуск Edge-агента {CAMERA_ID}. Анализ видеопотока...")
    
    while True:
        try:
            
            frame = capture_frame()
            
            
            detected_objects = run_cv_inference(frame)
            
            
            if detected_objects:
                
                payload = {
                    "stage_id": ACTIVE_STAGE_ID,
                    "detected_objects": detected_objects,
                    "calculated_volume": 0.0 
                }
                
                
                response = requests.post(API_URL, json=payload, timeout=5)
                
                if response.status_code == 200:
                    logging.info(f"Телеметрия отправлена: {len(detected_objects)} объектов")
                else:
                    logging.error(f"Ошибка API: {response.text}")
                    
        except requests.exceptions.RequestException as e:
            logging.error(f"Нет связи с сервером: {e}. Данные можно сохранить локально и отправить позже.")
            
        
        
        time.sleep(5)

if __name__ == "__main__":
    main_loop()