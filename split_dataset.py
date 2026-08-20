"""
Script untuk split dataset YOLO ke training (70%), testing (20%), evaluation (10%).
Setiap kelas di-split secara proporsional, image + label selalu berpasangan.
"""

import os
import shutil
import random

# ==================== KONFIGURASI ====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Folder sumber masing-masing kelas
# Perhatikan: Kelas 0 folder labelnya 'label' (singular), kelas lain 'labels' (plural)
KELAS_DIRS = {
    "Kelas 0 - Hole":         {"images": "images", "labels": "label"},
    "Kelas 1 - Object":       {"images": "images", "labels": "labels"},
    "Kelas 2 - Oil Spot":     {"images": "images", "labels": "labels"},
    "Kelas 3 - Thread Error": {"images": "images", "labels": "labels"},
}

# Folder output
OUTPUT_DIR = os.path.join(BASE_DIR, "Dataset Splited")

# Rasio split
TRAIN_RATIO = 0.70
TEST_RATIO  = 0.20
EVAL_RATIO  = 0.10

# Seed untuk reproducibility
RANDOM_SEED = 42

# =====================================================


def get_paired_files(images_dir, labels_dir):
    """
    Cari semua pasangan image-label berdasarkan nama file (tanpa ekstensi).
    Hanya file yang punya pasangan lengkap (image + label) yang diambil.
    """
    # Kumpulkan semua image files
    image_files = {}
    for f in os.listdir(images_dir):
        name, ext = os.path.splitext(f)
        if ext.lower() in ('.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff', '.webp'):
            image_files[name] = f

    # Kumpulkan semua label files
    label_files = {}
    for f in os.listdir(labels_dir):
        name, ext = os.path.splitext(f)
        if ext.lower() == '.txt':
            label_files[name] = f

    # Cari yang berpasangan
    paired = []
    unpaired_images = []
    unpaired_labels = []

    all_names = set(image_files.keys()) | set(label_files.keys())
    for name in sorted(all_names):
        has_image = name in image_files
        has_label = name in label_files
        if has_image and has_label:
            paired.append((image_files[name], label_files[name]))
        elif has_image:
            unpaired_images.append(image_files[name])
        else:
            unpaired_labels.append(label_files[name])

    return paired, unpaired_images, unpaired_labels


def split_list(items, train_ratio, test_ratio, eval_ratio):
    """Split list menjadi 3 bagian sesuai rasio."""
    total = len(items)
    train_count = int(total * train_ratio)
    test_count = int(total * test_ratio)
    eval_count = total - train_count - test_count  # Sisanya ke eval agar tidak ada yang hilang

    train_set = items[:train_count]
    test_set = items[train_count:train_count + test_count]
    eval_set = items[train_count + test_count:]

    return train_set, test_set, eval_set


def copy_files(file_pairs, src_images_dir, src_labels_dir, dst_images_dir, dst_labels_dir):
    """Copy pasangan image-label ke folder tujuan."""
    for img_file, lbl_file in file_pairs:
        src_img = os.path.join(src_images_dir, img_file)
        src_lbl = os.path.join(src_labels_dir, lbl_file)
        dst_img = os.path.join(dst_images_dir, img_file)
        dst_lbl = os.path.join(dst_labels_dir, lbl_file)

        shutil.copy2(src_img, dst_img)
        shutil.copy2(src_lbl, dst_lbl)


def main():
    random.seed(RANDOM_SEED)

    # Buat folder output
    splits = {
        "training":   {"images": os.path.join(OUTPUT_DIR, "training", "images"),
                       "labels": os.path.join(OUTPUT_DIR, "training", "labels")},
        "testing":    {"images": os.path.join(OUTPUT_DIR, "testing", "images"),
                       "labels": os.path.join(OUTPUT_DIR, "testing", "labels")},
        "evaluation": {"images": os.path.join(OUTPUT_DIR, "evaluation", "images"),
                       "labels": os.path.join(OUTPUT_DIR, "evaluation", "labels")},
    }

    for split_name, paths in splits.items():
        os.makedirs(paths["images"], exist_ok=True)
        os.makedirs(paths["labels"], exist_ok=True)

    print("=" * 60)
    print("DATASET SPLITTER - YOLO Format")
    print(f"Rasio: Training {TRAIN_RATIO*100:.0f}% | Testing {TEST_RATIO*100:.0f}% | Evaluation {EVAL_RATIO*100:.0f}%")
    print("=" * 60)

    total_train = 0
    total_test = 0
    total_eval = 0
    total_all = 0

    for kelas_name, subfolder in KELAS_DIRS.items():
        kelas_dir = os.path.join(BASE_DIR, kelas_name)
        images_dir = os.path.join(kelas_dir, subfolder["images"])
        labels_dir = os.path.join(kelas_dir, subfolder["labels"])

        # Cek folder ada
        if not os.path.isdir(images_dir):
            print(f"\n[ERROR] Folder images tidak ditemukan: {images_dir}")
            continue
        if not os.path.isdir(labels_dir):
            print(f"\n[ERROR] Folder labels tidak ditemukan: {labels_dir}")
            continue

        # Ambil pasangan file
        paired, unpaired_imgs, unpaired_lbls = get_paired_files(images_dir, labels_dir)

        print(f"\n--- {kelas_name} ---")
        print(f"  Total pasangan image-label: {len(paired)}")

        if unpaired_imgs:
            print(f"  [WARNING] {len(unpaired_imgs)} image TANPA label: {unpaired_imgs[:5]}...")
        if unpaired_lbls:
            print(f"  [WARNING] {len(unpaired_lbls)} label TANPA image: {unpaired_lbls[:5]}...")

        # Shuffle untuk randomisasi
        random.shuffle(paired)

        # Split
        train_set, test_set, eval_set = split_list(paired, TRAIN_RATIO, TEST_RATIO, EVAL_RATIO)

        print(f"  Training:   {len(train_set)} ({len(train_set)/len(paired)*100:.1f}%)")
        print(f"  Testing:    {len(test_set)} ({len(test_set)/len(paired)*100:.1f}%)")
        print(f"  Evaluation: {len(eval_set)} ({len(eval_set)/len(paired)*100:.1f}%)")

        # Verifikasi tidak ada yang hilang
        assert len(train_set) + len(test_set) + len(eval_set) == len(paired), \
            f"FATAL: Jumlah split ({len(train_set)}+{len(test_set)}+{len(eval_set)}) != total ({len(paired)})"

        # Copy files
        copy_files(train_set, images_dir, labels_dir,
                   splits["training"]["images"], splits["training"]["labels"])
        copy_files(test_set, images_dir, labels_dir,
                   splits["testing"]["images"], splits["testing"]["labels"])
        copy_files(eval_set, images_dir, labels_dir,
                   splits["evaluation"]["images"], splits["evaluation"]["labels"])

        total_train += len(train_set)
        total_test += len(test_set)
        total_eval += len(eval_set)
        total_all += len(paired)

    # ==================== VERIFIKASI AKHIR ====================
    print("\n" + "=" * 60)
    print("RINGKASAN AKHIR")
    print("=" * 60)
    print(f"  Total data semua kelas: {total_all}")
    print(f"  Training:   {total_train} ({total_train/total_all*100:.1f}%)")
    print(f"  Testing:    {total_test} ({total_test/total_all*100:.1f}%)")
    print(f"  Evaluation: {total_eval} ({total_eval/total_all*100:.1f}%)")
    print(f"  TOTAL SPLIT: {total_train + total_test + total_eval}")

    assert total_train + total_test + total_eval == total_all, \
        "FATAL: Ada data yang hilang saat split!"

    # Verifikasi file di folder output
    print("\n--- Verifikasi File di Output ---")
    for split_name, paths in splits.items():
        n_images = len(os.listdir(paths["images"]))
        n_labels = len(os.listdir(paths["labels"]))
        status = "OK" if n_images == n_labels else "MISMATCH!"
        print(f"  {split_name}: {n_images} images, {n_labels} labels [{status}]")

        if n_images != n_labels:
            print(f"    [ERROR] Jumlah images dan labels tidak sama!")

    # Verifikasi setiap image punya label dan sebaliknya
    print("\n--- Verifikasi Pasangan Image-Label ---")
    all_ok = True
    for split_name, paths in splits.items():
        img_names = {os.path.splitext(f)[0] for f in os.listdir(paths["images"])}
        lbl_names = {os.path.splitext(f)[0] for f in os.listdir(paths["labels"])}

        missing_labels = img_names - lbl_names
        missing_images = lbl_names - img_names

        if missing_labels:
            print(f"  [ERROR] {split_name}: {len(missing_labels)} image tanpa label!")
            all_ok = False
        if missing_images:
            print(f"  [ERROR] {split_name}: {len(missing_images)} label tanpa image!")
            all_ok = False

    if all_ok:
        print("  Semua pasangan image-label LENGKAP di semua split!")

    print(f"\nOutput disimpan di: {OUTPUT_DIR}")
    print("SELESAI!")


if __name__ == "__main__":
    main()
