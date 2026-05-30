from api_reader import ApiReader
import time

if __name__ == "__main__":
    malopolska_bbox = (49.15, 50.55, 19.05, 21.35)
    # test obecnej implementacji apireader
    with ApiReader(malopolska_bbox) as reader:
        reader.start_receiving(interval_ms=10000)

        i=0

        while i<5:
            print(reader.latest_data)
            time.sleep(11)
            i+=1


        reader.stop_receiving()