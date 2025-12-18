# scp_gui.py
import tkinter as tk
from tkinter import ttk

from scp_signal_model import scpSignalModel
from scp_controller import scpController


def run_gui(controller: scpController, model: scpSignalModel) -> None:
    root = tk.Tk()
    root.title("Oscilloscope (UI)")

    # -------------------------
    # Controls
    # -------------------------
    frm = ttk.Frame(root, padding=10)
    frm.pack(fill="both", expand=True)

    # Buttons
    btn_frame = ttk.Frame(frm)
    btn_frame.pack(fill="x", pady=(0, 10))

    start_btn = ttk.Button(btn_frame, text="Start", command=controller.start)
    stop_btn = ttk.Button(btn_frame, text="Stop", command=controller.stop)
    start_btn.pack(side="left", padx=(0, 8))
    stop_btn.pack(side="left")

    # Inputs
    inputs = ttk.Frame(frm)
    inputs.pack(fill="x", pady=(0, 10))

    sample_time_var = tk.StringVar(value="1.0")  # ms
    sample_for_var = tk.StringVar(value="10.0")  # s
    scale_var = tk.StringVar(value="1.0")
    offset_var = tk.StringVar(value="0.0")

    def apply_fields():
        try:
            controller.set_sample_time_ms(float(sample_time_var.get()))
            controller.set_sample_for_s(float(sample_for_var.get()))
            controller.set_scale(float(scale_var.get()))
            controller.set_offset(float(offset_var.get()))
        except Exception:
            pass

    ttk.Label(inputs, text="sampleTime (ms):").grid(row=0, column=0, sticky="w")
    ttk.Entry(inputs, textvariable=sample_time_var, width=10).grid(row=0, column=1, padx=6)
    ttk.Label(inputs, text="sampleFor (s):").grid(row=0, column=2, sticky="w")
    ttk.Entry(inputs, textvariable=sample_for_var, width=10).grid(row=0, column=3, padx=6)

    ttk.Label(inputs, text="scale:").grid(row=1, column=0, sticky="w")
    ttk.Entry(inputs, textvariable=scale_var, width=10).grid(row=1, column=1, padx=6)
    ttk.Label(inputs, text="offset:").grid(row=1, column=2, sticky="w")
    ttk.Entry(inputs, textvariable=offset_var, width=10).grid(row=1, column=3, padx=6)

    apply_btn = ttk.Button(inputs, text="Apply", command=apply_fields)
    apply_btn.grid(row=0, column=4, rowspan=2, padx=(10, 0))

    # -------------------------
    # Simple scrolling plot (Canvas polyline)
    # -------------------------
    canvas = tk.Canvas(frm, width=900, height=300, bg="white")
    canvas.pack(fill="both", expand=True)

    status = ttk.Label(frm, text="Ready")
    status.pack(anchor="w", pady=(8, 0))

    def draw():
        canvas.delete("all")
        t, y = model.get_series()
        if len(t) < 2:
            root.after(50, draw)
            return

        # display last N points
        N = 400
        t = t[-N:]
        y = y[-N:]

        w = int(canvas.winfo_width())
        h = int(canvas.winfo_height())

        ymin, ymax = min(y), max(y)
        if abs(ymax - ymin) < 1e-9:
            ymax = ymin + 1e-9

        # map to canvas coords
        pts = []
        for i in range(len(y)):
            x = int(i * (w - 20) / max(1, (len(y) - 1))) + 10
            # invert y
            yy = (y[i] - ymin) / (ymax - ymin)
            ypix = int((h - 20) * (1.0 - yy)) + 10
            pts.extend([x, ypix])

        # axes
        canvas.create_line(10, h//2, w-10, h//2, fill="#ccc")
        canvas.create_rectangle(10, 10, w-10, h-10, outline="#ddd")

        canvas.create_line(*pts, fill="black", width=2)

        status.config(
            text=f"running={controller.is_running()}  points={len(model.get_series()[0])}  "
                 f"sampleTime={controller.config.sample_time_s*1000:.3f}ms  "
                 f"sampleFor={controller.config.sample_for_s:.2f}s  "
                 f"scale={controller.config.scale:.2f}  offset={controller.config.offset:.2f}"
        )

        root.after(50, draw)  # non-blocking UI refresh

    draw()
    root.mainloop()
