from api_reader import ApiReader
from db_manager import DBmanager
import time
import queue

if __name__ == "__main__":    
    malopolska_bbox = (49.15, 50.55, 19.05, 21.35)
    q = queue.Queue()
    db = DBmanager()

    # test obecnej implementacji apireader
    with ApiReader(bbox=malopolska_bbox,data_queue=q) as reader:
        reader.start_receiving(interval_s=10)

        i=0

        while i<5:
            try:
                nowe_dane = q.get(timeout=15)
                q.task_done()
                
            except queue.Empty:
                print("[Main] Nie otrzymano danych w czasie 15 sekund.")

            i+=1


        reader.stop_receiving()