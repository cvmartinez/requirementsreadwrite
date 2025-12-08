# OLD
# from .reader import Reader
# from .writer import Writer
# from .ftdi_device import FtdiDevice
# from .wavegen import Wave

# NEW
import json
import threading
import time

from .reader import Reader
from .writer import Writer
from .file_device import FileDevice
from .mic_device import MicrophoneDevice
from .wavegen import Wave


class ScriptRunner:
    """
    Executes a JSON script with commands:
      start, wait, stop, read, write
    Example:
    {
      "sequence": [
        { "start": { "mode": "acquire",
                     "in": "ftdi://::/1",
                     "out": "capture.bin",
                     "fs": 1000,
                     "n": 1024,
                     "loops": 10,
                     "chunk": 512 } },
        { "wait":  { "seconds": 2 } },
        { "stop":  {} },
        { "write": { "out": "ftdi://::/1",
                     "fo": 2000,
                     "n": 2048,
                     "wave": "square",
                     "amp": 1.0,
                     "chunk": 512 } }
      ]
    }
    """

    def __init__(self, script_path: str):
        self.script_path = script_path
        self._bg = None  # background thread

    def run(self):
        with open(self.script_path, "r") as f:
            doc = json.load(f)
        seq = doc.get("sequence", [])
        for step in seq:
            if not isinstance(step, dict) or len(step) != 1:
                print(f"[WARN] Bad step: {step}")
                continue
            cmd, params = next(iter(step.items()))
            params = params or {}
            cmd = cmd.lower()
            print(f"\n[ScriptRunner] {cmd.upper()}")
            if cmd == "start":
                self._start(params)
            elif cmd == "wait":
                self._wait(params)
            elif cmd == "stop":
                self._stop()
            elif cmd == "read":
                self._read(params)
            elif cmd == "write":
                self._write(params)
            else:
                print(f"[WARN] Unknown command: {cmd}")
        print("\n[ScriptRunner] Done.")

    # ---- handlers ----
    def _start(self, p):
        mode = (p.get("mode") or "acquire").lower()
        in_url = p.get("in")
        out = p.get("out")
        fs = p.get("fs")
        fo = p.get("fo")
        n = p.get("n")
        loops = p.get("loops")
        chunk = p.get("chunk", 512)
        amp = p.get("amp", 1.0)
        wave_name = (p.get("wave") or "sine").lower()
        w = {"sine": Wave.SINE, "square": Wave.SQUARE,
             "triangle": Wave.TRIANGLE}.get(wave_name, Wave.SINE)

        src = p.get("in", "")
        if isinstance(src, str) and src.lower().startswith("mic"):
            dev = MicrophoneDevice()
        else:
            dev = FileDevice()

        def worker():
            if mode == "acquire":
                Reader().run(
                    dev=dev,
                    in_path=in_url,
                    out_path=out,
                    fs=float(fs) if fs is not None else None,
                    n=int(n) if n is not None else None,
                    loops=int(loops) if loops is not None else None,
                    chunk=int(chunk),
                )
            elif mode == "generate":
                Writer().run(
                    dev=dev,
                    out_path=out,                 # FTDI URL for output device
                    fo=float(fo) if fo is not None else None,
                    wave=w,
                    amp=float(amp),
                    n=int(n) if n is not None else None,
                    loops=int(loops) if loops is not None else None,
                    chunk=int(chunk),
                )
            else:
                print(
                    f"[WARN] start.mode must be acquire|generate (got {mode})")
        self._bg = threading.Thread(target=worker, daemon=True)
        self._bg.start()
        print(f"[ScriptRunner] START launched (mode={mode}).")

    def _wait(self, p):
        secs = p.get("seconds")
        loops = p.get("loops")
        if secs is not None:
            print(f"[ScriptRunner] WAIT {secs}s")
            time.sleep(float(secs))
        elif loops is not None:
            print(f"[ScriptRunner] WAIT loops={loops} (simulated)")
            time.sleep(float(loops) * 0.1)
        else:
            print("[ScriptRunner] WAIT needs seconds or loops")

    def _stop(self):
        if self._bg and self._bg.is_alive():
            print("[ScriptRunner] STOP waiting for background job to finish...")
            self._bg.join(timeout=5)
            self._bg = None
            print("[ScriptRunner] STOP complete.")
        else:
            print("[ScriptRunner] No active background job.")

    def _read(self, p):
        print("[ScriptRunner] READ (one-shot)")
        src = p.get("in", "")
        if isinstance(src, str) and src.lower().startswith("mic"):
            dev = MicrophoneDevice()
        else:
            dev = FileDevice()

        Reader().run(
            dev=dev,
            in_path=p.get("in"),
            out_path=p.get("out"),
            fs=float(p.get("fs")) if p.get("fs") is not None else None,
            n=int(p.get("n")) if p.get("n") is not None else None,
            loops=int(p.get("loops")) if p.get("loops") is not None else None,
            chunk=int(p.get("chunk", 512)),
        )

    def _write(self, p):
        print("[ScriptRunner] WRITE (one-shot)")
        src = p.get("in", "")
        if isinstance(src, str) and src.lower().startswith("mic"):
            dev = MicrophoneDevice()
        else:
            dev = FileDevice()

        wave_name = (p.get("wave") or "sine").lower()
        w = {"sine": Wave.SINE, "square": Wave.SQUARE,
             "triangle": Wave.TRIANGLE}.get(wave_name, Wave.SINE)
        Writer().run(
            dev=dev,
            out_path=p.get("out"),                 # FTDI URL
            fo=float(p.get("fo")) if p.get("fo") is not None else None,
            wave=w,
            amp=float(p.get("amp", 1.0)),
            n=int(p.get("n")) if p.get("n") is not None else None,
            loops=int(p.get("loops")) if p.get("loops") is not None else None,
            chunk=int(p.get("chunk", 512)),
        )
