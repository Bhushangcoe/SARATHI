
"""SARATHI HUD with microphone, Groq, Piper and task confirmations."""

import math
import threading
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

from voice.listener import listen
from voice.speaker import speak, preload_voices, stop_speaking
from core.assistant import get_response

WIDTH = 760
HEIGHT = 500

BG = "#070A0F"
PANEL = "#0D121A"
TEXT = "#E8F1FF"
MUTED = "#718096"
CYAN = "#00E5FF"
GREEN = "#35F28B"
ORANGE = "#FFB84D"
BORDER = "#1C2A36"


class SarathiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SARATHI")
        self.root.geometry(f"{WIDTH}x{HEIGHT}")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)
        self.root.protocol("WM_DELETE_WINDOW", self.shutdown)

        self.is_listening = False
        self.is_speaking = False
        self.is_processing = False
        self.is_shutting_down = False

        self.animation_angle = 0
        self.pulse = 0
        self.activity_lines = []

        self._build_ui()
        self.root.bind("<space>", self.interrupt)

        threading.Thread(
            target=preload_voices,
            daemon=True,
        ).start()

        self.root.after(700, self.start_intro)
        self.root.after(50, self.animate)
        self.update_clock()

    # --------------------------------------------------------
    # BUILD USER INTERFACE
    # --------------------------------------------------------
    def _build_ui(self):
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=18, pady=(12, 5))

        tk.Label(
            header,
            text="S A R A T H I",
            font=("Segoe UI", 17, "bold"),
            bg=BG,
            fg=TEXT,
        ).pack(side="left")

        tk.Label(
            header,
            text="  V4  •  AI TASK CORE",
            font=("Consolas", 8, "bold"),
            bg=BG,
            fg=CYAN,
        ).pack(side="left", padx=8)

        self.clock_label = tk.Label(
            header,
            text="",
            font=("Consolas", 9),
            bg=BG,
            fg=MUTED,
        )
        self.clock_label.pack(side="right")

        main = tk.Frame(self.root, bg=BG)
        main.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=5,
        )

        # Left system panel
        left = tk.Frame(
            main,
            bg=PANEL,
            highlightbackground=BORDER,
            highlightthickness=1,
            width=145,
        )
        left.pack(side="left", fill="y", padx=(0, 8))
        left.pack_propagate(False)

        tk.Label(
            left,
            text="SYSTEM",
            font=("Consolas", 8, "bold"),
            bg=PANEL,
            fg=MUTED,
        ).pack(anchor="w", padx=12, pady=(13, 10))

        self.system_items = {}

        self._system_item(left, "CORE", "ONLINE")
        self._system_item(left, "GROQ", "ONLINE")
        self._system_item(left, "PIPER", "READY")
        self._system_item(left, "MIC", "READY")
        self._system_item(left, "MEMORY", "ACTIVE")
        self._system_item(left, "AGENT", "READY")

        # Center animation panel
        center = tk.Frame(
            main,
            bg=PANEL,
            highlightbackground=BORDER,
            highlightthickness=1,
        )
        center.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 8),
        )

        self.canvas = tk.Canvas(
            center,
            width=330,
            height=290,
            bg=PANEL,
            highlightthickness=0,
        )
        self.canvas.pack(pady=(8, 0))

        self.status_label = tk.Label(
            center,
            text="READY",
            font=("Consolas", 15, "bold"),
            bg=PANEL,
            fg=GREEN,
        )
        self.status_label.pack(pady=(0, 3))

        self.substatus_label = tk.Label(
            center,
            text="Press Space to interrupt",
            font=("Segoe UI", 8),
            bg=PANEL,
            fg=MUTED,
        )
        self.substatus_label.pack()

        # Right activity panel
        right = tk.Frame(
            main,
            bg=PANEL,
            highlightbackground=BORDER,
            highlightthickness=1,
            width=205,
        )
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        tk.Label(
            right,
            text="ACTIVITY",
            font=("Consolas", 8, "bold"),
            bg=PANEL,
            fg=MUTED,
        ).pack(anchor="w", padx=12, pady=(13, 8))

        self.activity_text = tk.Text(
            right,
            bg=PANEL,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            borderwidth=0,
            font=("Consolas", 8),
            wrap="word",
            state="disabled",
        )
        self.activity_text.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(0, 10),
        )

        # Footer
        footer = tk.Frame(self.root, bg=BG)
        footer.pack(fill="x", padx=18, pady=(2, 12))

        self.footer_label = tk.Label(
            footer,
            text="SARATHI • ONLINE",
            font=("Consolas", 8, "bold"),
            bg=BG,
            fg=CYAN,
        )
        self.footer_label.pack(side="left")

        tk.Label(
            footer,
            text="SPACE  •  STOP VOICE",
            font=("Consolas", 8),
            bg=BG,
            fg=MUTED,
        ).pack(side="right")

    def _system_item(self, parent, name, value):
        frame = tk.Frame(parent, bg=PANEL)
        frame.pack(fill="x", padx=12, pady=5)

        tk.Label(
            frame,
            text="●",
            font=("Segoe UI", 7),
            bg=PANEL,
            fg=GREEN,
        ).pack(side="left")

        tk.Label(
            frame,
            text=name,
            font=("Consolas", 8),
            bg=PANEL,
            fg=TEXT,
        ).pack(side="left", padx=5)

        value_label = tk.Label(
            frame,
            text=value,
            font=("Consolas", 7),
            bg=PANEL,
            fg=MUTED,
        )
        value_label.pack(side="right")

        self.system_items[name] = value_label

    # --------------------------------------------------------
    # STATUS AND ACTIVITY
    # --------------------------------------------------------
    def set_status(self, status, color=None, substatus=None):
        color = color or TEXT

        self.status_label.config(
            text=status,
            fg=color,
        )

        if substatus:
            self.substatus_label.config(text=substatus)

        self.footer_label.config(text=f"SARATHI • {status}")

    def log_activity(self, text):
        timestamp = datetime.now().strftime("%H:%M:%S")

        self.activity_lines.append(
            f"[{timestamp}] {text}"
        )

        if len(self.activity_lines) > 16:
            self.activity_lines.pop(0)

        self.activity_text.config(state="normal")
        self.activity_text.delete("1.0", "end")
        self.activity_text.insert(
            "end",
            "\n".join(self.activity_lines),
        )
        self.activity_text.see("end")
        self.activity_text.config(state="disabled")

    # --------------------------------------------------------
    # INTRODUCTION
    # --------------------------------------------------------
    def start_intro(self):
        if self.is_shutting_down:
            return

        self.set_status(
            "STARTING",
            CYAN,
            "Initializing voice system...",
        )

        self.log_activity("SARATHI initialized.")

        threading.Thread(
            target=self.intro_thread,
            daemon=True,
        ).start()

    def intro_thread(self):
        try:
            speak(
                "Hello Bhushan. I am Sarathi, your personal AI assistant. "
                "How can I help you?"
            )
        except Exception as error:
            print(f"[SARATHI] Intro error: {error}")

        if not self.is_shutting_down:
            try:
                self.root.after(500, self.begin_listening)
            except tk.TclError:
                pass

    # --------------------------------------------------------
    # MICROPHONE LISTENING
    # --------------------------------------------------------
    def begin_listening(self):
        if (
            self.is_shutting_down
            or self.is_speaking
            or self.is_processing
            or self.is_listening
        ):
            return

        self.is_listening = True

        self.set_status(
            "LISTENING",
            CYAN,
            "Speak now...",
        )

        self.system_items["MIC"].config(
            text="LISTEN",
            fg=CYAN,
        )

        self.log_activity("Microphone active.")

        threading.Thread(
            target=self.listen_thread,
            daemon=True,
        ).start()

    def listen_thread(self):
        try:
            result = listen()

            if isinstance(result, dict):
                text = result.get("text", "")
            else:
                text = str(result or "")

        except Exception as error:
            print(f"[SARATHI] Listener error: {error}")
            text = ""

        try:
            self.root.after(
                0,
                lambda captured=text: self.process_input(captured),
            )
        except tk.TclError:
            pass

    # --------------------------------------------------------
    # PROCESS USER INPUT
    # --------------------------------------------------------
    def process_input(self, text):
        self.is_listening = False

        if self.is_shutting_down:
            return

        self.system_items["MIC"].config(
            text="READY",
            fg=MUTED,
        )

        text = str(text or "").strip()

        if not text:
            self.set_status(
                "READY",
                GREEN,
                "I didn't hear anything.",
            )

            self.log_activity("No speech detected.")
            self.root.after(800, self.begin_listening)
            return

        self.log_activity(f"You: {text}")

        self.is_processing = True

        self.set_status(
            "THINKING",
            ORANGE,
            "SARATHI is thinking...",
        )

        self.system_items["GROQ"].config(
            text="THINKING",
            fg=ORANGE,
        )

        threading.Thread(
            target=self.response_thread,
            args=(text,),
            daemon=True,
        ).start()

    # --------------------------------------------------------
    # TASK CONFIRMATION
    # Show the dialog on Tkinter's main thread.
    # --------------------------------------------------------
    def confirm_task(self, message):
        if self.is_shutting_down:
            return False

        result = {"approved": False}
        completed = threading.Event()

        def show_confirmation():
            try:
                if not self.is_shutting_down:
                    result["approved"] = messagebox.askyesno(
                        "SARATHI — Confirm Action",
                        f"{message}\n\nDo you want to continue?",
                        parent=self.root,
                    )

            except Exception as error:
                print(f"[SARATHI] Confirmation error: {error}")
                result["approved"] = False

            finally:
                completed.set()

        try:
            self.root.after(0, show_confirmation)

        except (tk.TclError, RuntimeError) as error:
            print(
                f"[SARATHI] Could not request confirmation: {error}"
            )
            return False

        if not completed.wait(timeout=120):
            print("[SARATHI] Confirmation timed out.")
            return False

        return bool(result["approved"])

    # --------------------------------------------------------
    # GET RESPONSE
    # --------------------------------------------------------
    def response_thread(self, text):
        try:
            response = get_response(
                text,
                confirm_callback=self.confirm_task,
            )

        except Exception as error:
            print(f"[SARATHI] Response error: {error}")
            response = "Something went wrong while I was thinking."

        try:
            self.root.after(
                0,
                lambda reply=response: self.speak_response(reply),
            )
        except tk.TclError:
            pass

    # --------------------------------------------------------
    # SPEAK RESPONSE
    # --------------------------------------------------------
    def speak_response(self, response):
        if self.is_shutting_down:
            return

        self.is_processing = False
        self.is_speaking = True

        self.system_items["GROQ"].config(
            text="ONLINE",
            fg=GREEN,
        )

        self.system_items["PIPER"].config(
            text="SPEAK",
            fg=CYAN,
        )

        self.set_status(
            "SPEAKING",
            CYAN,
            "Press Space to interrupt",
        )

        self.log_activity(f"SARATHI: {response}")

        threading.Thread(
            target=self.speech_thread,
            args=(response,),
            daemon=True,
        ).start()

    def speech_thread(self, response):
        try:
            speak(response)

        except Exception as error:
            print(f"[SARATHI] Speech error: {error}")

        try:
            self.root.after(0, self.speech_finished)
        except tk.TclError:
            pass

    def speech_finished(self):
        self.is_speaking = False

        self.system_items["PIPER"].config(
            text="READY",
            fg=MUTED,
        )

        if self.is_shutting_down:
            return

        self.set_status(
            "READY",
            GREEN,
            "Listening again...",
        )

        self.root.after(650, self.begin_listening)

    # --------------------------------------------------------
    # SPACEBAR TO STOP SPEECH
    # --------------------------------------------------------
    def interrupt(self, event=None):
        if not self.is_speaking:
            return

        print("[SARATHI] Speech interrupted.")
        stop_speaking()

        self.is_speaking = False

        self.system_items["PIPER"].config(
            text="READY",
            fg=MUTED,
        )

        self.set_status(
            "READY",
            GREEN,
            "Voice interrupted.",
        )

        self.log_activity("Voice interrupted.")

        if not self.is_shutting_down:
            self.root.after(400, self.begin_listening)

    # --------------------------------------------------------
    # HUD ANIMATION
    # --------------------------------------------------------
    def animate(self):
        if self.is_shutting_down:
            return

        self.animation_angle += 3
        self.pulse += 0.08

        self.canvas.delete("all")

        center_x = 165
        center_y = 135

        # Outer rings
        for radius in (92, 76, 58):
            self.canvas.create_oval(
                center_x - radius,
                center_y - radius,
                center_x + radius,
                center_y + radius,
                outline=BORDER,
                width=1,
            )

        # Pulsing core
        pulse_size = 35 + math.sin(self.pulse) * 5

        self.canvas.create_oval(
            center_x - pulse_size,
            center_y - pulse_size,
            center_x + pulse_size,
            center_y + pulse_size,
            outline=CYAN,
            width=2,
        )

        core_size = 20

        self.canvas.create_oval(
            center_x - core_size,
            center_y - core_size,
            center_x + core_size,
            center_y + core_size,
            fill=CYAN,
            outline="",
        )

        # Rotating dots
        for i in range(12):
            angle = math.radians(
                self.animation_angle + i * 30
            )

            radius = 105

            x = center_x + math.cos(angle) * radius
            y = center_y + math.sin(angle) * radius
            size = 2 + (i % 3)

            self.canvas.create_oval(
                x - size,
                y - size,
                x + size,
                y + size,
                fill=CYAN,
                outline="",
            )

        # Animated waveform
        base_y = 255
        points = []

        for x in range(35, 296, 8):
            wave = math.sin(
                x * 0.08 + self.pulse * 2
            )

            if self.is_listening:
                amplitude = 18
            elif self.is_speaking:
                amplitude = 12
            elif self.is_processing:
                amplitude = 8
            else:
                amplitude = 4

            points.append(
                (x, base_y + wave * amplitude)
            )

        for i in range(len(points) - 1):
            self.canvas.create_line(
                points[i][0],
                points[i][1],
                points[i + 1][0],
                points[i + 1][1],
                fill=CYAN,
                width=2,
            )

        self.root.after(40, self.animate)

    # --------------------------------------------------------
    # CLOCK AND SHUTDOWN
    # --------------------------------------------------------
    def update_clock(self):
        if self.is_shutting_down:
            return

        now = datetime.now()

        self.clock_label.config(
            text=now.strftime("%d %b %Y  •  %I:%M:%S %p")
        )

        self.root.after(1000, self.update_clock)

    def shutdown(self):
        if self.is_shutting_down:
            return

        self.is_shutting_down = True

        try:
            stop_speaking()
        except Exception:
            pass

        try:
            self.root.destroy()
        except tk.TclError:
            pass


def main():
    root = tk.Tk()
    SarathiApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
