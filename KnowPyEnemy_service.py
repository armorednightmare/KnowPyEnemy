from KnowPyEnemy import KpyEconfig, process_zevtc_files
import colorama
import time
from colorama import Fore, init

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

colorama.init()
dbg = False

def process_file(file):

    if all(wrd in file for wrd in ['zevtc', 'WvW']):
        print(" processing started ")

        for count in range(10):
            try:
                process_zevtc_files(KpyEconf, [file])
                break
            except OSError:
                print("waiting for file to be accessible...")
                time.sleep(1)
                continue

class MyHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        if dbg:
            print(event.event_type, event.src_path.strip(), Fore.RESET)

    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith('zevtc'):
            process_file(event.src_path.strip())

    def on_moved(self, event):
        if event.is_directory:
            return
        if event.dest_path.endswith('zevtc'):
            process_file(event.dest_path.strip())

if __name__ == "__main__":

    KpyEconf = KpyEconfig()
    KpyEconf.read_config()

    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path=KpyEconf.ARCDPS_LOG_LOCATION, recursive=True)
    observer.start()
    input("press ENTER to end observer service\n")
    observer.stop()
    input('Press ENTER to exit')
