import threading
import time

stop_flag = False

def worker():
    while not stop_flag:
        # Do some work
        print("Working...")
        time.sleep(0.5)
    print("Exiting thread gracefully.")

t = threading.Thread(target=worker)
t.start()

time.sleep(3)
stop_flag = True
t.join()  # Wait for the thread to finish
print("Thread stopped.")
