# scope_mt/scope.py
import sys
import threading

from .stop_token import StopToken
from .mic_device import MicrophoneDevice
from .timer_thread import TimerThread
from .reader_thread import ReaderThread


class ScopeApp:
    def __init__(self):
        self.out_lock = threading.Lock()

    def run(self, sample_ms, wait_s):
        stop = StopToken()

        # Use microphone as the input device instead of FTDI
        # sample_interval is how often we read from the mic
        sample_interval_s = sample_ms / 1000.0

        # Create the device – default system mic
        dev = MicrophoneDevice(samplerate=44100, channels=1)

        timer = TimerThread(wait_s, stop, self.out_lock)
        reader = ReaderThread(dev, sample_interval_s, stop, self.out_lock)

        with self.out_lock:
            print(
                f"[main] start scope (mic): sample={sample_ms}ms wait={wait_s}s")

        reader.start()
        timer.start()

        timer.join()
        stop.stop()
        reader.join()

        print("[main] scope finished")


def parse_command(argv):
    tokens = argv[1:]
    if tokens[0] != "start" or tokens[-1] != "stop":
        raise SystemExit("Usage: scope start sampleTime=1ms wait=5s stop")

    sample_ms = None
    wait_s = None

    for tok in tokens[1:-1]:
        t = tok.replace(" ", "")
        if t.startswith("sampleTime="):
            sample_ms = int(t.split("=")[1][:-2])
        if t.startswith("wait="):
            wait_s = int(t.split("=")[1][:-1])

    if sample_ms is None or wait_s is None:
        raise SystemExit(
            "Error: Both sampleTime=Xms and wait=Ys are required.\n"
            "Example: scope start sampleTime=1ms wait=5s stop"
        )

    return sample_ms, wait_s


def main(argv):
    sample_ms, wait_s = parse_command(argv)
    ScopeApp().run(sample_ms, wait_s)


if __name__ == "__main__":
    main(sys.argv)
