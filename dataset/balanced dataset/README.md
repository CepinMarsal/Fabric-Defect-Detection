# TILDA V2 Balanced Dataset
Balanced version of the TILDA V2 Fabric Defect Dataset used for the Fabric Defect Detection project.

## Dataset Overview
This dataset contains fabric images with YOLO-format bounding box annotations for four defect classes:
- Hole
- Objects
- Oil Spot
- Thread Error
The original dataset contains 896 images with an imbalanced class distribution.

## Balancing Process
To meet the requirement of equal data distribution across classes, 200 images were selected for each class using random sampling with a fixed random seed (`42`).

Final dataset:
- Hole: 200 images
- Objects: 200 images
- Oil Spot: 200 images
- Thread Error: 200 images

Total: **800 images**

## Dataset Split
The balanced dataset is divided into:
- Training: 560 images (70%)
- Validation: 160 images (20%)
- Testing: 80 images (10%)

Distribution per class:
| Class | Train | Validation | Test | Total |
|---|---:|---:|---:|---:|
| Hole | 140 | 40 | 20 | 200 |
| Objects | 140 | 40 | 20 | 200 |
| Oil Spot | 140 | 40 | 20 | 200 |
| Thread Error | 140 | 40 | 20 | 200 |
| **Total** | **560** | **160** | **80** | **800** |

## Annotation Format
The dataset uses YOLO annotation format.
Each image has a corresponding `.txt` label file containing:

```text
class_id x_center y_center width height