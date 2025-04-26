from typing import List

import numpy as np


def get_moves_from_screen(
    screen: np.ndarray,
    green_thresh: int = 230,
) -> List[str]:
    """
    screen: HxW  NumPy array, here H=600, W=100.
    green_thresh: green channel value to threshold branch pixels.
    Return 6 moves: 'right' if block has a left branch, else 'left'.
    """

    H, W = screen.shape
    assert H % 6 == 0, "Height must be divisible by 6, got {}".format(H)

    block_h = H // 6

    # Reshape into (6,block_h,W) so blocks[i] is the i‑th branch from the top (stack)
    blocks = screen.reshape(6, block_h, W)

    # Keep only the bottom 40 rows of each block (crops). It is either a branch or sky
    greens = blocks[:, -40:, :]  # shape=(6, 40, 100)
    print("Greens shape:", greens.shape)

    block_means = greens.mean(axis=(1, 2))  # shape (6,)
    # print for debug to adjust green_thresh, e.g. [202.5, 202.5, 244.4, ...]
    print("Block mean greens:", block_means)

    # Branches actually have a lower green value than the sky
    is_left_branch = block_means < green_thresh

    # Map to safe moves: branch on left --> move right; else move left
    moves = ["right" if b else "left" for b in is_left_branch]

    return moves[::-1]  # Return in natural order from bottom to top


if __name__ == "__main__":
    import time

    import cv2

    start = time.perf_counter()
    img = cv2.imread("assets/screen-20250421-220705-529.png")[:, :, 1]
    moves = get_moves_from_screen(img)
    duration = time.perf_counter() - start
    print(f"Captured {img.shape} in {duration * 1000:.6f} ms")
    print(moves)
    assert moves == ["left", "right", "right", "left", "right", "right"]
