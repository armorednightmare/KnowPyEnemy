import KnowPyEnemy as KpyE
import colorama
from colorama import Fore, init

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

colorama.init()
dbg = False

def process_file(file):

    if 'zevtc' in file:
        zevtc_files = KpyE.find_zevtc_files(folder,'WvW')[0]

        print(" processing started ")
        KpyE.process_zevtc_files([zevtc_files])

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

event_handler = MyHandler()
observer = Observer()
folder = r"D:\Documents\Guild Wars 2\addons\arcdps\arcdps.cbtlogs"
observer.schedule(event_handler, path=folder, recursive=True)
observer.start()

input("press ENTER to end observer service\n")
observer.stop()
input('Press ENTER to exit')





