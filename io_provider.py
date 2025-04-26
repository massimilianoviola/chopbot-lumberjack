import configparser
import os
import time

import mss
import numpy as np
from pynput.keyboard import Controller, Key


class IOProvider:
    """Capture a configured region of the screen and interact with the keyboard at super high speed."""

    def __init__(self, cfg: configparser.ConfigParser) -> None:
        # IO sources
        self.keyboard = Controller()
        self.sct = mss.mss()

        # Part of the screen to capture
        r = cfg["region"]
        mon = self.sct.monitors[r.getint("monitor_number")]
        self.monitor = {
            "top": mon["top"] + r.getint("top"),
            "left": mon["left"] + r.getint("left"),
            "width": r.getint("width"),
            "height": r.getint("height"),
            "mon": r.getint("monitor_number"),
        }

        self.key_delay = cfg["bot"].getfloat("key_delay", 0.01)

        # Debugging
        dbg = cfg["debug"]
        self.debug = dbg.getboolean("enabled")
        self.debug_dir = dbg.get("directory", "")
        if self.debug and self.debug_dir:
            os.makedirs(self.debug_dir, exist_ok=True)

    def get_screenshot(self) -> np.ndarray:
        """
        Grab the region of interest nd return a HxW NumPy array of the green channel (uint8).
        If debugging is enabled, also write a timestamped PNG.
        """
        frame = self.sct.grab(self.monitor)

        # Dump a PNG
        if self.debug:
            timestamp = time.strftime("%Y%m%d-%H%M%S") + f"-{int(time.time() * 1000) % 1000}"
            filename = os.path.join(self.debug_dir, f"screen-{timestamp}.png")
            mss.tools.to_png(frame.rgb, frame.size, output=filename)

        green_channel = np.array(frame)[:, :, 1]  # HxW

        return green_channel

    def hit_key(self, key: str) -> None:
        """Hit a keyboard key twice, pausing after each tap to give the OS time to process."""
        k = Key.left if key.lower() == "left" else Key.right
        for _ in range(2):
            self.keyboard.tap(k)
            time.sleep(self.key_delay)


if __name__ == "__main__":
    cfg = configparser.ConfigParser()
    cfg.read("config.ini")
    # Always turn on debugging for a test run, to adjust the region
    cfg["debug"]["enabled"] = "true"

    io = IOProvider(cfg)
    start = time.perf_counter()
    screenshot = io.get_screenshot()
    duration = time.perf_counter() - start
    print(f"Captured {screenshot.shape} in {duration * 1000:.1f} ms")

    io.hit_key("left")
