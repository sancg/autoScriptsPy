import re
import argparse
from pathlib import Path
from collections import defaultdict

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--folder", required=True)


def find_video_files(root_folder):
    root = Path(root_folder).expanduser()
    video_extensions = {".mp4", ".mkv", ".avi", ".mov"}

    for file in root.rglob("*"):
        if file.suffix.lower() in video_extensions:
            yield file


def extract_id(fs_name):
    matches = re.findall(r"\[([^\]]+)\]", fs_name)
    return matches[-1] if matches else None


def collect_video_ids(root_folder):
    ids = defaultdict(list)
    for file in find_video_files(root_folder):

        video_id = extract_id(file.name)

        if video_id:
            ids[video_id].append(file)

    return ids


def find_duplicates(ids_dict):

    duplicates = {
        video_id: paths for video_id, paths in ids_dict.items() if len(paths) > 1
    }

    return duplicates


def main():
    args = parser.parse_args()

    ids = collect_video_ids(args.folder)

    print("Total unique IDs:", len(ids))

    duplicates = find_duplicates(ids)

    print("Duplicate IDs:", len(duplicates))

    for video_id, paths in duplicates.items():
        print(f"\nDuplicate ID: {video_id}")

        for p in paths:
            print("  ", p)


main()
