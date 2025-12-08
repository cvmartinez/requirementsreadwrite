import threading
import time


class TimerThread(threading.Thread):
    def __init__(self, duration_s, stop_token, out_lock):
        super().__init__(daemon=True)
        self.duration_s = duration_s
        self.stop_token = stop_token
        self.out_lock = out_lock

    def run(self):
        deadline = time.monotonic() + self.duration_s
        remaining = int(self.duration_s)

        while True:
            if time.monotonic() >= deadline or self.stop_token.stopped():
                break

            with self.out_lock:
                print(f"[timer] {remaining} s left")

            time.sleep(1.0)
            remaining -= 1

        with self.out_lock:
            print("[timer] done")

        self.stop_token.stop()
