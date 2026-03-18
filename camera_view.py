#!/usr/bin/env python3
import argparse
import __main__

import cv2
from pop import Camera


def parse_args():
    parser = argparse.ArgumentParser(description="POP camera viewer")
    parser.add_argument("--width", type=int, default=640, help="Display width")
    parser.add_argument("--height", type=int, default=480, help="Display height")
    parser.add_argument("--cap-mode", type=int, default=2, choices=[0, 1, 2, 3, 4], help="Camera capture mode")
    parser.add_argument("--flip", default="2", help="nvvidconv flip-method value")
    parser.add_argument("--window", default="POP Camera", help="OpenCV window title")
    return parser.parse_args()


def main():
    args = parse_args()

    # POP camera pipeline reads this variable from __main__
    __main__._camera_flip_method = str(args.flip)

    cam = None
    try:
        cam = Camera(width=args.width, height=args.height, cap_mode=args.cap_mode)
        while cam.loop:
            cam.show(args.window)
    except RuntimeError as exc:
        print(f"[ERROR] Camera init/read failed: {exc}")
        print("Hint: check camera connection and Docker device/runtime options.")
    except KeyboardInterrupt:
        pass
    finally:
        if cam is not None:
            try:
                cam.destroy()
            except Exception:
                pass
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
