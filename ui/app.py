import tkinter as tk
import threading
import math

from voice.listener import listen
from voice.speaker import speak, preload_voices, stop_speaking
from core.assistant import get_response


# ============================================================
# COLORS
# ============================================================

BG_COLOR = "#05070A"
PANEL_COLOR = "#0A0F14"

CYAN = "#00E5FF"
BLUE = "#008CFF"
WHITE = "#EAFBFF"
GRAY = "#71808C"

GREEN = "#00FF9C"
AMBER = "#FFB000"
RED = "#FF3B30"


# ============================================================
# SARATHI APPLICATION
# ============================================================

class SarathiApp:

    def __init__(self, root):

        self.root = root

        # ----------------------------------------------------
        # PRELOAD VOICE MODEL IN BACKGROUND (speed fix)
        #
        # Starts loading the Piper voice model immediately,
        # in parallel with the UI building below, so it's
        # already warmed up by the time the intro needs to speak.
        # ----------------------------------------------------

        threading.Thread(
            target=preload_voices,
            daemon=True
        ).start()

        # ----------------------------------------------------
        # WINDOW
        # ----------------------------------------------------

        self.root.title("SARATHI AI")

        self.root.geometry(
            "900x650"
        )

        self.root.configure(
            bg=BG_COLOR
        )

        self.root.minsize(
            800,
            600
        )

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close_app
        )

        # ----------------------------------------------------
        # KEY-PRESS INTERRUPT
        #
        # Press Spacebar to immediately stop Sarathi mid-sentence.
        # Using a key instead of the mic to interrupt avoids the
        # mic picking up her own voice through your speakers.
        # ----------------------------------------------------

        self.root.bind(
            "<space>",
            self.interrupt_speaking
        )

        self.root.focus_set()

        # ----------------------------------------------------
        # STATE
        # ----------------------------------------------------

        self.is_running = True
        self.is_listening = False
        self.is_speaking = False

        self.animation_angle = 0
        self.pulse_value = 0

        # ----------------------------------------------------
        # MAIN FRAME
        # ----------------------------------------------------

        self.main_frame = tk.Frame(
            self.root,
            bg=BG_COLOR
        )

        self.main_frame.pack(
            fill="both",
            expand=True
        )

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        self.title_label = tk.Label(
            self.main_frame,
            text="SARATHI",
            font=("Segoe UI", 30, "bold"),
            fg=CYAN,
            bg=BG_COLOR
        )

        self.title_label.pack(
            pady=(25, 2)
        )

        # ----------------------------------------------------
        # SUBTITLE
        # ----------------------------------------------------

        self.subtitle_label = tk.Label(
            self.main_frame,
            text="PERSONAL AI ASSISTANT",
            font=("Segoe UI", 10),
            fg=GRAY,
            bg=BG_COLOR
        )

        self.subtitle_label.pack(
            pady=(0, 10)
        )

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        self.status_label = tk.Label(
            self.main_frame,
            text="INITIALIZING",
            font=("Segoe UI", 11, "bold"),
            fg=AMBER,
            bg=BG_COLOR
        )

        self.status_label.pack(
            pady=(5, 10)
        )

        # ----------------------------------------------------
        # HUD CANVAS
        # ----------------------------------------------------

        self.canvas = tk.Canvas(
            self.main_frame,
            width=600,
            height=360,
            bg=BG_COLOR,
            highlightthickness=0
        )

        self.canvas.pack(
            pady=5
        )

        # ----------------------------------------------------
        # INFO PANEL
        # ----------------------------------------------------

        self.info_frame = tk.Frame(
            self.main_frame,
            bg=PANEL_COLOR,
            highlightbackground="#13202A",
            highlightthickness=1
        )

        self.info_frame.pack(
            fill="x",
            padx=60,
            pady=(10, 20)
        )

        self.info_label = tk.Label(
            self.info_frame,
            text="English voice mode",
            font=("Segoe UI", 10),
            fg=GRAY,
            bg=PANEL_COLOR
        )

        self.info_label.pack(
            pady=10
        )

        # ----------------------------------------------------
        # FOOTER
        # ----------------------------------------------------

        self.footer_label = tk.Label(
            self.main_frame,
            text='Speak naturally • English only • Say "Bye Sarathi" to exit',
            font=("Segoe UI", 9),
            fg=GRAY,
            bg=BG_COLOR
        )

        self.footer_label.pack(
            pady=(0, 10)
        )

        # ----------------------------------------------------
        # START HUD ANIMATION
        # ----------------------------------------------------

        self.animate_hud()

        # ----------------------------------------------------
        # START SARATHI AFTER UI LOADS
        # ----------------------------------------------------

        self.root.after(
            800,
            self.start_sarathi
        )

    # ========================================================
    # KEY-PRESS INTERRUPT
    # ========================================================

    def interrupt_speaking(self, event=None):
        """
        Called when Spacebar is pressed. Immediately stops whatever
        Sarathi is currently saying. The background speak thread's
        own finally block takes care of resetting state and moving
        back to listening, once stop_speaking() cuts the audio.
        """

        if not self.is_running:
            return

        if self.is_speaking:

            stop_speaking()

            self.set_status(
                "interrupted",
                RED
            )

    # ========================================================
    # STATUS
    # ========================================================

    def set_status(
        self,
        text,
        color=CYAN
    ):

        if not self.is_running:
            return

        self.root.after(
            0,
            lambda: self._update_status(
                text,
                color
            )
        )

    def _update_status(
        self,
        text,
        color
    ):

        if not self.is_running:
            return

        self.status_label.config(
            text=text.upper(),
            fg=color
        )

    # ========================================================
    # START SARATHI
    # ========================================================

    def start_sarathi(self):

        if not self.is_running:
            return

        self.set_status(
            "starting",
            AMBER
        )

        threading.Thread(
            target=self.intro_in_background,
            daemon=True
        ).start()

    # ========================================================
    # INTRO
    # ========================================================

    def intro_in_background(self):

        intro = (
            "Hello Bhushan. "
            "I am Sarathi, your personal AI assistant. "
            "How can I help you?"
        )

        print(
            f"SARATHI: {intro}"
        )

        self.is_speaking = True

        try:

            speak(
                intro
            )

        except Exception as error:

            print(
                "\nSARATHI intro voice error:"
            )

            print(error)

        finally:

            self.is_speaking = False

            if self.is_running:

                self.root.after(
                    0,
                    self.start_listening
                )

    # ========================================================
    # START LISTENING
    # ========================================================

    def start_listening(self):

        if not self.is_running:
            return

        if self.is_listening:
            return

        self.is_listening = True

        if self.is_speaking:

            self.set_status(
                "listening (say anything to interrupt)",
                GREEN
            )

        else:

            self.set_status(
                "listening",
                CYAN
            )

        threading.Thread(
            target=self.listen_in_background,
            daemon=True
        ).start()

    # ========================================================
    # LISTEN IN BACKGROUND
    # ========================================================

    def listen_in_background(self):

        try:

            user_data = listen()

            if not self.is_running:
                return

            self.root.after(
                0,
                self.handle_voice_result,
                user_data
            )

        except Exception as error:

            print(
                "\nSARATHI listener error:"
            )

            print(error)

            self.is_listening = False

            if self.is_running:

                self.set_status(
                    "listener error",
                    RED
                )

                self.root.after(
                    1500,
                    self.start_listening
                )

    # ========================================================
    # HANDLE VOICE RESULT
    # ========================================================

    def handle_voice_result(
        self,
        user_data
    ):

        self.is_listening = False

        if not self.is_running:
            return

        # ----------------------------------------------------
        # GET TEXT
        # ----------------------------------------------------

        if isinstance(
            user_data,
            dict
        ):

            user_message = user_data.get(
                "text",
                ""
            )

        else:

            user_message = str(
                user_data or ""
            )

        user_message = user_message.strip()

        # ----------------------------------------------------
        # NOTHING HEARD
        # ----------------------------------------------------

        if not user_message:

            self.set_status(
                "no input",
                AMBER
            )

            self.root.after(
                700,
                self.start_listening
            )

            return

        # ----------------------------------------------------
        # PRINT USER MESSAGE
        # ----------------------------------------------------

        print(
            f"User: {user_message}"
        )

        message = user_message.lower().strip()

        # ----------------------------------------------------
        # SHUTDOWN COMMANDS
        # ----------------------------------------------------

        shutdown_commands = [
            "bye sarathi",
            "goodbye sarathi",
            "sarathi stop",
            "stop sarathi",
            "go offline",
            "shut down sarathi",
            "shutdown sarathi",
            "exit sarathi"
        ]

        if any(
            command in message
            for command in shutdown_commands
        ):

            # Interrupt her mid-sentence if she was already speaking.
            if self.is_speaking:
                stop_speaking()

            self.is_speaking = True

            self.set_status(
                "shutting down",
                AMBER
            )

            threading.Thread(
                target=self.shutdown_in_background,
                daemon=True
            ).start()

            return

        # ----------------------------------------------------
        # GET RESPONSE
        #
        # IMPORTANT:
        #
        # get_response() accepts ONE argument.
        #
        # Correct:
        # get_response(user_message)
        #
        # ----------------------------------------------------

        # BARGE-IN: if Sarathi was already speaking, cut her off
        # immediately before responding to this new message.
        if self.is_speaking:
            stop_speaking()
            self.is_speaking = False

        try:

            response = get_response(
                user_message
            )

        except Exception as error:

            print(
                "\nSARATHI brain error:"
            )

            print(error)

            response = (
                "Sorry, I ran into a problem "
                "while processing that."
            )

        # ----------------------------------------------------
        # PRINT SARATHI RESPONSE
        # ----------------------------------------------------

        print(
            f"SARATHI: {response}"
        )

        # ----------------------------------------------------
        # SPEAK RESPONSE
        # ----------------------------------------------------

        self.is_speaking = True

        self.set_status(
            "responding",
            AMBER
        )

        threading.Thread(
            target=self.speak_in_background,
            args=(response,),
            daemon=True
        ).start()

        # Keep listening immediately, even while she's still speaking,
        # so a new question can interrupt her (barge-in).
        self.root.after(
            200,
            self.start_listening
        )

    # ========================================================
    # SPEAK IN BACKGROUND
    # ========================================================

    def speak_in_background(
        self,
        response
    ):

        try:

            speak(
                response
            )

        except Exception as error:

            print(
                "\nSARATHI speech error:"
            )

            print(error)

        finally:

            self.is_speaking = False

            # NOTE: no call to start_listening/ready_to_listen here -
            # continuous listening is already running independently
            # (kicked off right after dispatching this speak thread), so
            # calling it again here would create a duplicate loop.

    # ========================================================
    # SHUTDOWN
    # ========================================================

    def shutdown_in_background(self):

        goodbye = (
            "Bye Bhushan. "
            "See you soon."
        )

        print(
            f"SARATHI: {goodbye}"
        )

        try:

            speak(
                goodbye
            )

        except Exception as error:

            print(
                "\nSARATHI shutdown voice error:"
            )

            print(error)

        finally:

            if self.is_running:

                self.root.after(
                    0,
                    self.close_app
                )

    # ========================================================
    # CLOSE APPLICATION
    # ========================================================

    def close_app(self):

        if not self.is_running:
            return

        self.is_running = False
        self.is_listening = False
        self.is_speaking = False

        try:

            self.root.destroy()

        except Exception:

            pass

    # ========================================================
    # HUD ANIMATION
    # ========================================================

    def animate_hud(self):

        if not self.is_running:
            return

        self.canvas.delete(
            "all"
        )

        center_x = 300
        center_y = 180

        # ----------------------------------------------------
        # PULSE
        # ----------------------------------------------------

        self.pulse_value += 0.08

        pulse = (
            math.sin(
                self.pulse_value
            ) + 1
        ) / 2

        # ----------------------------------------------------
        # OUTER RINGS
        # ----------------------------------------------------

        for i in range(5):

            radius = (
                105
                + i * 22
                + pulse * 8
            )

            if i == 0:

                outline = CYAN

            elif i == 1:

                outline = BLUE

            else:

                outline = "#123545"

            self.canvas.create_oval(
                center_x - radius,
                center_y - radius,
                center_x + radius,
                center_y + radius,
                outline=outline,
                width=2 if i < 2 else 1
            )

        # ----------------------------------------------------
        # ROTATING ARCS
        # ----------------------------------------------------

        self.animation_angle += 3

        for i in range(3):

            start_angle = (
                self.animation_angle
                + i * 120
            ) % 360

            radius = (
                125
                + i * 12
            )

            self.canvas.create_arc(
                center_x - radius,
                center_y - radius,
                center_x + radius,
                center_y + radius,
                start=start_angle,
                extent=55,
                style=tk.ARC,
                outline=(
                    CYAN
                    if i == 0
                    else BLUE
                ),
                width=2
            )

        # ----------------------------------------------------
        # MAIN CORE
        # ----------------------------------------------------

        core_radius = (
            58
            + pulse * 8
        )

        self.canvas.create_oval(
            center_x - core_radius,
            center_y - core_radius,
            center_x + core_radius,
            center_y + core_radius,
            fill="#07151D",
            outline=CYAN,
            width=3
        )

        # ----------------------------------------------------
        # INNER CORE
        # ----------------------------------------------------

        inner_radius = (
            30
            + pulse * 5
        )

        self.canvas.create_oval(
            center_x - inner_radius,
            center_y - inner_radius,
            center_x + inner_radius,
            center_y + inner_radius,
            fill="#0B2430",
            outline=BLUE,
            width=2
        )

        # ----------------------------------------------------
        # SARATHI LETTER
        # ----------------------------------------------------

        self.canvas.create_text(
            center_x,
            center_y - 5,
            text="S",
            font=(
                "Segoe UI",
                30,
                "bold"
            ),
            fill=WHITE
        )

        # ----------------------------------------------------
        # SARATHI TEXT
        # ----------------------------------------------------

        self.canvas.create_text(
            center_x,
            center_y + 28,
            text="SARATHI",
            font=(
                "Segoe UI",
                8,
                "bold"
            ),
            fill=CYAN
        )

        # ----------------------------------------------------
        # STATUS INDICATOR
        # ----------------------------------------------------

        if self.is_listening:

            self.canvas.create_text(
                center_x,
                center_y + 125,
                text="● LISTENING",
                font=(
                    "Segoe UI",
                    10,
                    "bold"
                ),
                fill=GREEN
            )

        elif self.is_speaking:

            self.canvas.create_text(
                center_x,
                center_y + 125,
                text="● SPEAKING",
                font=(
                    "Segoe UI",
                    10,
                    "bold"
                ),
                fill=AMBER
            )

        else:

            self.canvas.create_text(
                center_x,
                center_y + 125,
                text="● STANDBY",
                font=(
                    "Segoe UI",
                    10,
                    "bold"
                ),
                fill=GRAY
            )

        # ----------------------------------------------------
        # NEXT FRAME
        # ----------------------------------------------------

        self.root.after(
            40,
            self.animate_hud
        )


# ============================================================
# MAIN
# ============================================================

def main():

    root = tk.Tk()

    SarathiApp(
        root
    )

    root.mainloop()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()