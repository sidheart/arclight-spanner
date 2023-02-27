#!/usr/bin/python3
# A simple multithreaded program that resizes images to 4K resolution

from PIL import Image
import argparse
import os
import sys
import threading
import time
import concurrent.futures

RESOLUTION_4k = (3840, 2160)
LOADING_ANIMATION = "⣾⣷⣯⣟⡿⢿⣻⣽"
N_WORKERS = 5


loading_keyframe = 0
num_images = 0
num_processed = 0
files_to_delete = []


def print_progress():
    global loading_keyframe, num_images, num_processed
    while True:
        sys.stdout.write(
            "\r{} {:.2f}% Complete".format(
                LOADING_ANIMATION[loading_keyframe], (num_processed / num_images) * 100
            )
        )
        loading_keyframe = (loading_keyframe + 1) % (len(LOADING_ANIMATION))
        time.sleep(0.2)


def resize_image(path: str, cleanup: bool):
    global num_processed
    try:
        im = Image.open(path)
        im = im.resize(size=RESOLUTION_4k, resample=Image.HAMMING)
        file_name, file_extension = os.path.splitext(path)
        im.save(file_name + "_4k" + file_extension)
        if cleanup:
            files_to_delete.append(path)
    except:
        print(f"Exception processing image: {path}")
    finally:
        num_processed += 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="image-processor", description="atm it just resizes images",
    )
    parser.add_argument("directory")
    parser.add_argument('--cleanup', action='store_true')
    args = parser.parse_args()
    with concurrent.futures.ThreadPoolExecutor(max_workers=N_WORKERS) as executor:
        with os.scandir(args.directory) as it:
            for entry in it:
                if not entry.name.startswith(".") and entry.is_file():
                    executor.submit(resize_image, entry.path, args.cleanup)
                    num_images += 1
        # progress bar
        threading.Thread(target=print_progress, daemon=True).start()
    if args.cleanup:
        for file in files_to_delete:
            os.remove(file)
    
