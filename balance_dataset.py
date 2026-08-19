"""
Script untuk membalance dataset2 menjadi 300 gambar per kelas,
lalu menyimpannya ke folder dataset2_balanced dengan penamaan:
  - hole:         0-1.png, 0-2.png, ..., 0-300.png
  - object:       1-1.png, 1-2.png, ..., 1-300.png
  - oil spot:     2-1.png, 2-2.png, ..., 2-300.png
  - thread error: 3-1.png, 3-2.png, ..., 3-300.png
"""

import os
import shutil
import random

# Konfigurasi
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_DIR = os.path.join(BASE_DIR, "dataset2")
OUTPUT_DIR = os.path.join(BASE_DIR, "dataset2_balanced")
SAMPLES_PER_CLASS = 300

# Mapping: (index kelas, nama folder sumber, nama folder tujuan)
CLASS_MAP = [
    (0, "hole",         "hole"),
    (1, "objects",      "object"),
    (2, "oil spot",     "oil spot"),
    (3, "thread error", "thread error"),
]

# Seed untuk reproducibility
random.seed(42)

def main():
    # Buat folder output utama
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for class_idx, src_folder_name, dst_folder_name in CLASS_MAP:
        src_path = os.path.join(SOURCE_DIR, src_folder_name)
        dst_path = os.path.join(OUTPUT_DIR, dst_folder_name)
        os.makedirs(dst_path, exist_ok=True)

        # Ambil semua file gambar dari folder sumber
        all_files = sorted([
            f for f in os.listdir(src_path)
            if os.path.isfile(os.path.join(src_path, f))
        ])

        print(f"Kelas '{dst_folder_name}' (index {class_idx}): {len(all_files)} gambar ditemukan")

        if len(all_files) < SAMPLES_PER_CLASS:
            print(f"  WARNING: Hanya ada {len(all_files)} gambar, kurang dari {SAMPLES_PER_CLASS}!")
            selected = all_files
        else:
            # Ambil 300 gambar secara random
            selected = random.sample(all_files, SAMPLES_PER_CLASS)

        # Salin dan rename file
        for i, filename in enumerate(selected, start=1):
            # Ambil ekstensi asli
            _, ext = os.path.splitext(filename)
            # Nama baru: {class_idx}-{nomor}.{ext}
            new_name = f"{class_idx}-{i}{ext}"

            src_file = os.path.join(src_path, filename)
            dst_file = os.path.join(dst_path, new_name)
            shutil.copy2(src_file, dst_file)

        print(f"  -> {len(selected)} gambar disalin ke '{dst_folder_name}' sebagai {class_idx}-1{ext} ... {class_idx}-{len(selected)}{ext}")

    print(f"\nSelesai! Dataset balanced tersimpan di: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
