"""Split YOLO images and labels into class folders and rename each pair."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Pisahkan pasangan citra-label YOLO berdasarkan kelas."
    )
    parser.add_argument(
        "--images", type=Path, nargs="+", required=True, help="Satu atau beberapa folder citra sumber"
    )
    parser.add_argument(
        "--labels", type=Path, nargs="+", required=True, help="Satu atau beberapa folder label YOLO sumber"
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Folder output yang berisi Kelas 0 sampai Kelas 3",
    )
    parser.add_argument(
        "--move",
        action="store_true",
        help="Pindahkan file, bukan menyalinnya. Default: salin.",
    )
    return parser.parse_args()


def read_class(label_path: Path) -> int:
    classes = set()
    for line_number, line in enumerate(label_path.read_text(encoding="utf-8").splitlines(), 1):
        fields = line.split()
        if not fields:
            continue
        try:
            class_id = int(fields[0])
        except ValueError as error:
            raise ValueError(f"Kelas tidak valid di {label_path}:{line_number}") from error
        if class_id not in range(4):
            raise ValueError(f"Kelas harus 0-3 di {label_path}:{line_number}")
        classes.add(class_id)

    if len(classes) != 1:
        raise ValueError(f"Label harus memiliki tepat satu kelas: {label_path}")
    return classes.pop()


def transfer(source: Path, destination: Path, move: bool) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if move:
        shutil.move(str(source), str(destination))
    else:
        shutil.copy2(source, destination)


def split_dataset(images_dir: Path, labels_dir: Path, output_dir: Path, move: bool) -> None:
    images = sorted(
        path for path in images_dir.iterdir() if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )
    labels = {path.stem: path for path in labels_dir.glob("*.txt") if path.is_file()}
    counters = [0, 0, 0, 0]
    skipped = 0

    for image_path in images:
        label_path = labels.get(image_path.stem)
        if label_path is None:
            print(f"Lewati, label tidak ditemukan: {image_path.name}")
            skipped += 1
            continue

        class_id = read_class(label_path)
        counters[class_id] += 1
        new_stem = f"{class_id}-{counters[class_id]}"
        class_dir = output_dir / f"Kelas {class_id}"
        transfer(image_path, class_dir / "images" / f"{new_stem}{image_path.suffix.lower()}", move)
        transfer(label_path, class_dir / "label" / f"{new_stem}.txt", move)

    print("Selesai.")
    for class_id, count in enumerate(counters):
        print(f"Kelas {class_id}: {count} pasangan")
    if skipped:
        print(f"File citra tanpa pasangan yang dilewati: {skipped}")


def main() -> None:
    args = parse_args()
    if len(args.images) != len(args.labels):
        raise SystemExit("Jumlah folder citra dan folder label harus sama.")
    for images_dir, labels_dir in zip(args.images, args.labels):
        if not images_dir.is_dir():
            raise SystemExit(f"Folder citra tidak ditemukan: {images_dir}")
        if not labels_dir.is_dir():
            raise SystemExit(f"Folder label tidak ditemukan: {labels_dir}")
        split_dataset(images_dir, labels_dir, args.output, args.move)


if __name__ == "__main__":
    main()