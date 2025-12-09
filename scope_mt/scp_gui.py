import tkinter as tk
from tkinter import ttk
import threading
import queue
import time

from .scp_config import scpConfig
from .scp_signal_source import scpSignalSource
from .scp_pipeline import scpPipelineProcessor


class scpGuiView:
    """
    Tkinter-based GUI oscilloscope.

    This acts as an additional View in your architecture:
    - Reuses scpConfig, scpSignalSource, scpPipelineProcessor
    - Adds only GUI & drawing logic
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Python Oscilloscope GUI")
        self.root.configure(bg="#111111")

        # Core parameters (same idea as CLI)
        self.freq_hz = 2.0
        self.amplitude = 1.0
        self.sample_time = 0.001  # seconds
        self.duration_s = 5.0
        self.scale = 1.0
        self.offset = 0.0

        self.running = False
        self.worker: threading.Thread | None = None
        self.sample_queue: "queue.Queue[float]" = queue.Queue(maxsize=5000)
        self.y_values: list[float] = []

        # Model references (set in start_acquisition)
        self.config: scpConfig | None = None
        self.signal_source: scpSignalSource | None = None
        self.pipeline: scpPipelineProcessor | None = None

        # Canvas settings
        self.canvas_width = 800
        self.canvas_height = 320

        # Build UI
        self._build_header()
        self._build_canvas()
        self._build_controls()
        self._build_status()

        # Start GUI update loop
        self.root.after(30, self.update_canvas)

    # ------------------------------------------------------------------
    # UI BUILDERS
    # ------------------------------------------------------------------

    def _build_header(self) -> None:
        header = tk.Frame(self.root, bg="#111111")
        header.pack(fill=tk.X, pady=(10, 0))

        title = tk.Label(
            header,
            text="scpOscilloscope - GUI View",
            fg="#00ff88",
            bg="#111111",
            font=("Helvetica", 16, "bold"),
        )
        title.pack()

        subtitle = tk.Label(
            header,
            text="Live sine-wave visualization using scpConfig, scpSignalSource, scpPipelineProcessor",
            fg="#bbbbbb",
            bg="#111111",
            font=("Helvetica", 9),
        )
        subtitle.pack(pady=(2, 8))

    def _build_canvas(self) -> None:
        canvas_frame = tk.Frame(self.root, bg="#111111")
        canvas_frame.pack(padx=10, pady=(0, 10), fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(
            canvas_frame,
            width=self.canvas_width,
            height=self.canvas_height,
            bg="#000000",
            highlightthickness=1,
            highlightbackground="#333333",
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self._draw_grid()

    def _draw_grid(self) -> None:
        """Draws oscilloscope-style grid lines on the canvas."""
        self.canvas.delete("grid")
        w = self.canvas_width
        h = self.canvas_height

        # Vertical grid lines
        for x in range(0, w + 1, 50):
            self.canvas.create_line(
                x, 0, x, h,
                fill="#222222",
                width=1,
                tags="grid",
            )

        # Horizontal grid lines
        for y in range(0, h + 1, 40):
            self.canvas.create_line(
                0, y, w, y,
                fill="#222222",
                width=1,
                tags="grid",
            )

        # Center line
        mid_y = h // 2
        self.canvas.create_line(
            0, mid_y, w, mid_y,
            fill="#444444",
            width=1,
            dash=(4, 4),
            tags="grid",
        )

    def _build_controls(self) -> None:
        controls = tk.Frame(self.root, bg="#111111")
        controls.pack(fill=tk.X, padx=10, pady=(0, 10))

        # Left side: sliders
        sliders = tk.Frame(controls, bg="#111111")
        sliders.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Right side: Start/Stop buttons
        buttons = tk.Frame(controls, bg="#111111")
        buttons.pack(side=tk.RIGHT, padx=(10, 0))

        # Frequency
        self.freq_label_val = tk.StringVar(value=f"{self.freq_hz:.1f} Hz")
        self._make_slider_row(
            parent=sliders,
            text="Frequency",
            from_=0.5,
            to=20.0,
            initial=self.freq_hz,
            on_change=self._on_freq_change,
            value_var=self.freq_label_val,
        )

        # Amplitude
        self.amp_label_val = tk.StringVar(value=f"{self.amplitude:.2f}")
        self._make_slider_row(
            parent=sliders,
            text="Amplitude",
            from_=0.1,
            to=5.0,
            initial=self.amplitude,
            on_change=self._on_amp_change,
            value_var=self.amp_label_val,
        )

        # Sample time (ms)
        self.sample_label_val = tk.StringVar(value=f"{self.sample_time * 1000:.2f} ms")
        self._make_slider_row(
            parent=sliders,
            text="Sample Time (ms)",
            from_=0.1,
            to=5.0,
            initial=self.sample_time * 1000,
            on_change=self._on_sample_time_change,
            value_var=self.sample_label_val,
        )

        # Duration (s)
        self.duration_label_val = tk.StringVar(value=f"{self.duration_s:.1f} s")
        self._make_slider_row(
            parent=sliders,
            text="Duration (s)",
            from_=1.0,
            to=10.0,
            initial=self.duration_s,
            on_change=self._on_duration_change,
            value_var=self.duration_label_val,
        )

        # Scale
        self.scale_label_val = tk.StringVar(value=f"{self.scale:.2f}")
        self._make_slider_row(
            parent=sliders,
            text="Y Scale",
            from_=0.5,
            to=3.0,
            initial=self.scale,
            on_change=self._on_scale_change,
            value_var=self.scale_label_val,
        )

        # Offset
        self.offset_label_val = tk.StringVar(value=f"{self.offset:.2f}")
        self._make_slider_row(
            parent=sliders,
            text="Y Offset",
            from_=-2.0,
            to=2.0,
            initial=self.offset,
            on_change=self._on_offset_change,
            value_var=self.offset_label_val,
        )

        # Buttons: Start / Stop
        self.start_button = tk.Button(
            buttons,
            text="Start",
            width=10,
            bg="#00aa55",
            fg="#ffffff",
            activebackground="#00cc66",
            relief=tk.FLAT,
            command=self.start_acquisition,
        )
        self.start_button.pack(pady=4)

        self.stop_button = tk.Button(
            buttons,
            text="Stop",
            width=10,
            bg="#aa0033",
            fg="#ffffff",
            activebackground="#cc0044",
            relief=tk.FLAT,
            state=tk.DISABLED,
            command=self.stop_acquisition,
        )
        self.stop_button.pack(pady=4)

    def _make_slider_row(
        self,
        parent: tk.Frame,
        text: str,
        from_: float,
        to: float,
        initial: float,
        on_change,
        value_var: tk.StringVar,
    ) -> None:
        row = tk.Frame(parent, bg="#111111")
        row.pack(fill=tk.X, pady=2)

        label = tk.Label(
            row,
            text=text,
            fg="#dddddd",
            bg="#111111",
            width=16,
            anchor="w",
        )
        label.pack(side=tk.LEFT)

        slider = ttk.Scale(
            row,
            from_=from_,
            to=to,
            value=initial,
            orient=tk.HORIZONTAL,
            length=350,
            command=lambda v: on_change(float(v)),
        )
        slider.pack(side=tk.LEFT, padx=5)

        value_label = tk.Label(
            row,
            textvariable=value_var,
            fg="#aaaaaa",
            bg="#111111",
            width=10,
            anchor="e",
        )
        value_label.pack(side=tk.RIGHT)

    def _build_status(self) -> None:
        status_frame = tk.Frame(self.root, bg="#111111")
        status_frame.pack(fill=tk.X, padx=10, pady=(0, 8))

        self.status_label = tk.Label(
            status_frame,
            text="Status: Idle",
            fg="#bbbbbb",
            bg="#111111",
            anchor="w",
        )
        self.status_label.pack(side=tk.LEFT)

        self.info_label = tk.Label(
            status_frame,
            text="Ready",
            fg="#888888",
            bg="#111111",
            anchor="e",
        )
        self.info_label.pack(side=tk.RIGHT)

    # ------------------------------------------------------------------
    # SLIDER CALLBACKS
    # ------------------------------------------------------------------

    def _on_freq_change(self, value: float) -> None:
        self.freq_hz = value
        self.freq_label_val.set(f"{value:.1f} Hz")
        if self.running and self.signal_source is not None:
            self.signal_source.freq_hz = value

    def _on_amp_change(self, value: float) -> None:
        self.amplitude = value
        self.amp_label_val.set(f"{value:.2f}")
        if self.running and self.signal_source is not None:
            self.signal_source.amplitude = value

    def _on_sample_time_change(self, value: float) -> None:
        self.sample_time = value / 1000.0
        self.sample_label_val.set(f"{value:.2f} ms")

    def _on_duration_change(self, value: float) -> None:
        self.duration_s = value
        self.duration_label_val.set(f"{value:.1f} s")

    def _on_scale_change(self, value: float) -> None:
        self.scale = value
        self.scale_label_val.set(f"{value:.2f}")
        if self.running and self.pipeline is not None:
            self.pipeline.scale = value

    def _on_offset_change(self, value: float) -> None:
        self.offset = value
        self.offset_label_val.set(f"{value:.2f}")
        if self.running and self.pipeline is not None:
            self.pipeline.offset = value

    # ------------------------------------------------------------------
    # ACQUISITION CONTROL
    # ------------------------------------------------------------------

    def start_acquisition(self) -> None:
        if self.running:
            return

        self.config = scpConfig(
            sample_time=self.sample_time,
            duration=self.duration_s,
            scale=self.scale,
            offset=self.offset,
            freq_hz=self.freq_hz,
            amplitude=self.amplitude,
        )

        self.signal_source = scpSignalSource(
            self.config.freq_hz,
            self.config.amplitude,
            self.config.sample_time,
        )
        self.pipeline = scpPipelineProcessor(
            scale=self.config.scale,
            offset=self.config.offset,
        )

        self.y_values = []
        with self.sample_queue.mutex:
            self.sample_queue.queue.clear()

        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="Status: Running", fg="#00ff88")
        self.info_label.config(
            text=f"freq={self.freq_hz:.1f}Hz, amp={self.amplitude:.2f}, dt={self.sample_time*1000:.2f}ms"
        )

        self.worker = threading.Thread(target=self._acquisition_loop, daemon=True)
        self.worker.start()

    def stop_acquisition(self) -> None:
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Idle", fg="#bbbbbb")
        self.info_label.config(text="Stopped")

    def _acquisition_loop(self) -> None:
        start_t = time.time()
        next_t = start_t
        end_t = start_t + self.duration_s
        sample_time = self.sample_time

        while self.running and time.time() < end_t:
            raw = self.signal_source.next_sample()
            processed = self.pipeline.process(raw)

            try:
                self.sample_queue.put_nowait(processed)
            except queue.Full:
                pass

            next_t += sample_time
            sleep_t = next_t - time.time()
            if sleep_t > 0:
                time.sleep(sleep_t)

        self.running = False
        self.root.after(0, self._on_acquisition_finished)

    def _on_acquisition_finished(self) -> None:
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Idle", fg="#bbbbbb")
        self.info_label.config(text="Completed one capture window")

    # ------------------------------------------------------------------
    # DRAWING
    # ------------------------------------------------------------------

    def update_canvas(self) -> None:
        while not self.sample_queue.empty():
            self.y_values.append(self.sample_queue.get())

        max_points = 800
        if len(self.y_values) > max_points:
            self.y_values = self.y_values[-max_points:]

        self.canvas.delete("wave")
        self.canvas.delete("hud")

        if len(self.y_values) > 1:
            w = self.canvas_width
            h = self.canvas_height
            mid_y = h / 2
            amp_scale = h * 0.4

            n = len(self.y_values)
            points: list[float] = []
            for i, v in enumerate(self.y_values):
                x = (i / max(n - 1, 1)) * w
                y = mid_y - (v * amp_scale)
                points.extend([x, y])

            self.canvas.create_line(
                *points,
                fill="#00ff88",
                width=2,
                smooth=True,
                tags="wave",
            )

        hud_text = (
            f"freq={self.freq_hz:.1f}Hz  "
            f"amp={self.amplitude:.2f}  "
            f"scale={self.scale:.2f}  "
            f"offset={self.offset:.2f}"
        )
        self.canvas.create_text(
            10,
            10,
            text=hud_text,
            fill="#888888",
            font=("Helvetica", 9),
            anchor="nw",
            tags="hud",
        )

        self.root.after(30, self.update_canvas)


def main() -> None:
    root = tk.Tk()
    app = scpGuiView(root)
    root.mainloop()


if __name__ == "__main__":
    main()
