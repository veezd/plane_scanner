from opensky_api import OpenSkyApi
from db_manager import DBmanager
import threading
import time

class ApiReader:
    def __init__(self,bbox,data_queue): # boundingBox to chwilowa zmienna do testow (zeby oszczedzic tokeny)
        self.api = OpenSkyApi()
        self._stop_event = threading.Event()
        self._thread = None
        #self.latest_data = None # podlegac bedzie zmiana
        self.bounding_box = bbox # 4 elementowa krotka
        self.queue = data_queue

    # potrzebne do uzycia context managera ktory zarzadza polaczeniem http
    def __enter__(self):
        self.api.__enter__()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.api.__exit__(exc_type,exc_val,exc_tb)
        return None
    #

    def _read_loop(self,interval_s):
        while not self._stop_event.is_set():
            try:
                states = self.api.get_states(bbox=self.bounding_box)
                if states:
                    self.queue.put(states)
                    print(f"[ApiReader] Succesfully retrieved data from API")

            except Exception as e:
                print(f"[ApiReader] Data retrieval error : {e}")

            self._stop_event.wait(interval_s)

    def start_receiving(self,interval_s):
        if self._thread is not None and self._thread.is_alive():
            print("[ApiReader] Called 'start_receiving' while data retrieval is already in progress")
            return

        self._stop_event.clear()

        self._thread = threading.Thread(
            target = self._read_loop,
            args = (interval_s,), # implementacja Thread wymaga takiego dziwnego zapisu krotki
            daemon = True
        )

        self._thread.start()
        print(f"[ApiReader] Started data retrieval with interval {interval_s}s")


    def stop_receiving(self):
        if self._thread is None or not self._thread.is_alive():
            print("[ApiReader] Called 'stop_receiving' while data retrieval is offline")
            return
        
        print("[ApiReader] Stopping data retrieval thread")
        self._stop_event.set()
        self._thread.join()
        print("[ApiReader] Thread eliminated succesfully")
        return None