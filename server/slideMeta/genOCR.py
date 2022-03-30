from curses import raw
import os
import json
import cv2


from paddleocr import PaddleOCR

ocr_reader = PaddleOCR(lang='en')

def generate_ocr(path):
    images_path = os.path.join(path, "images")
    ocr_path = os.path.join(path, "ocr")
    if os.path.isdir(images_path) is False:
        return

    print("HERE: ", path)

    os.makedirs(ocr_path, exist_ok=True)
    for filename in os.listdir(images_path):
        if filename.endswith(".jpg"):
            image_path = os.path.join(images_path, filename)
            image = cv2.imread(image_path)
            image_size = {
                "height": image.shape[0],
                "width": image.shape[1]
            }

            with open(os.path.join(ocr_path, filename[:-4] + ".json"), "w") as f:
                raw_ocr_result = ocr_reader.ocr(image_path, cls=False)
                ocr_result = []
                for raw_result in raw_ocr_result:
                    bbox = raw_result[0]

                    for i in range(len(bbox)):
                        for j in range(len(bbox[i])):
                            bbox[i][j] = float(bbox[i][j])

                    text = raw_result[1][0]
                    conf = float(raw_result[1][1])
                    ocr_result.append({
                        "boundingBox": bbox,
                        "text": text,
                        "conf": conf, 
                    })

                json.dump({
                    "ocrResult": ocr_result,
                    "imageSize": image_size,
                }, fp=f, indent=2)

if __name__ == "__main__":
    for filename in os.listdir("./slideData"):
        parent_path = os.path.join("./slideData", filename)
        generate_ocr(parent_path)
