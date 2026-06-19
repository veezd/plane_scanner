from api_reader import ApiReader
from db_manager import DBmanager
import time
import queue

if __name__ == "__main__":
    q = queue.Queue()
    download_interval = 60

    db = DBmanager(queue=q, s_interval=download_interval+5)
    with ApiReader( data_queue=q, d_interval=download_interval) as reader:
        reader.start_receiving()
        db.begin_saving()

        try:
            while True:
                time.sleep(15)
        except KeyboardInterrupt:
            print("Stopping due to user interrupt")
        finally:
            reader.stop_receiving()
            db.end_saving()