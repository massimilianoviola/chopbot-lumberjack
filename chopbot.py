import configparser
import threading
import time

from pynput import keyboard

from io_provider import IOProvider
from moves import get_moves_from_screen


class ChopBot:
    """Orchestrate automatic play for the Lumberjack game, capturing frames, computing optimal moves, and simulating key presses."""

    def __init__(self, io_provider: IOProvider, screenshot_delay: float = 0.125):
        self.io_provider = io_provider
        self.screenshot_delay = screenshot_delay
        self.stop_event = threading.Event()

    @staticmethod
    def wait_for_start(timeout: float = 10.0) -> None:
        """Wait for the user to press Space or for a timeout (in seconds) before starting the bot."""
        start_event = threading.Event()

        def on_press(key):
            if key == keyboard.Key.space:
                start_event.set()
                return False  # stop listener

        listener = keyboard.Listener(on_press=on_press)
        listener.start()
        print(
            f"Switch to the game window now. Starting in {timeout:.0f}s or press Space to begin early..."
        )
        start_event.wait(timeout)
        listener.stop()

    def play(self):
        """Main loop to play the game. Captures screenshots, computes moves, and simulates key presses."""
        # Wait for user to press Space to start
        self.wait_for_start(timeout=10.0)

        # Setup stop listener
        def on_stop(key):
            if key == keyboard.Key.esc:
                self.stop_event.set()
                return False

        stop_listener = keyboard.Listener(on_press=on_stop)
        stop_listener.start()
        print("ChopBot running. Press Esc to stop...")

        try:
            while not self.stop_event.is_set():
                panel = self.io_provider.get_screenshot()
                moves = get_moves_from_screen(panel)
                for mv in moves:
                    self.io_provider.hit_key(mv)
                time.sleep(self.screenshot_delay)
        except Exception as e:
            print(f"Error during play: {e}")
        finally:
            stop_listener.stop()
            print("ChopBot stopped by user!")


if __name__ == "__main__":
    cfg = configparser.ConfigParser()
    cfg.read("config.ini")
    io = IOProvider(cfg)
    bot = ChopBot(io, screenshot_delay=cfg["bot"].getfloat("screenshot_delay"))
    bot.play()
