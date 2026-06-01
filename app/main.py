from api_reader import ApiReader
from db_manager import DBmanager
import time
import queue

if __name__ == "__main__":    
    malopolska_bbox = (49.15, 50.55, 19.05, 21.35)
    q = queue.Queue()
    download_interval = 10

    db = DBmanager(queue=q, s_interval=download_interval+5)
    # test obecnej implementacji apireader
    with ApiReader(bbox=malopolska_bbox,data_queue=q,d_interval=download_interval) as reader:
        reader.start_receiving()
        db.begin_saving()
        i=0

        while i<5:
            try:
                print("tura")      
                time.sleep(15) # czekamy 15 sekund na dane, powinno wystarczyć na 1-2 pobrania danych z API          
            except queue.Empty:
                print("[Main] Nie otrzymano danych w czasie 15 sekund.")

            i+=1


        reader.stop_receiving()
        db.end_saving()