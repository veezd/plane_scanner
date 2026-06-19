from opensky_api import OpenSkyApi
import threading
import json
import os

class ApiReader:
    def __init__(self, data_queue, d_interval, bbox=(49.0, 54.9, 14.1, 24.2)):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        repo_root = os.path.dirname(current_dir)
        creds_path = os.path.join(repo_root, "credentials.json")
        
        with open(creds_path, "r") as f:
            creds = json.load(f)
            
        client_id = creds.get("clientId")
        client_secret = creds.get("clientSecret")

        self.api = OpenSkyApi(client_id=client_id, client_secret=client_secret)
        self._stop_event = threading.Event()
        self._thread = None
        self.bounding_box = bbox
        self.queue = data_queue
        self.download_interval = d_interval
        
    def __enter__(self):
        self.api.__enter__()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.api.__exit__(exc_type, exc_val, exc_tb)
        return None

    def _read_loop(self):
        while not self._stop_event.is_set():
            try:
                states = self.api.get_states(bbox=self.bounding_box)
                if states:
                    self.queue.put(states)
                    print(f"[ApiReader] Succesfully retrieved data from API")

            except Exception as e:
                print(f"[ApiReader] Data retrieval error : {e}")

            self._stop_event.wait(self.download_interval)

    def start_receiving(self):
        if self._thread is not None and self._thread.is_alive():
            print("[ApiReader] Called 'start_receiving' while data retrieval is already in progress")
            return

        self._stop_event.clear()

        self._thread = threading.Thread(
            target=self._read_loop,
            daemon=True
        )

        self._thread.start()
        print(f"[ApiReader] Started data retrieval with interval {self.download_interval}s")

    def stop_receiving(self):
        if self._thread is None or not self._thread.is_alive():
            print("[ApiReader] Called 'stop_receiving' while data retrieval is offline")
            return
        
        print("[ApiReader] Stopping data retrieval thread")
        self._stop_event.set()
        self._thread.join()
        print("[ApiReader] Thread eliminated succesfully")
        return None