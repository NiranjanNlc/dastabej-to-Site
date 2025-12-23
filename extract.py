from paddleocr import PaddleOCR

ocr = PaddleOCR(
    lang="en",
    use_textline_orientation=True
)

img_path = "sample.jpg"

results = ocr.predict(img_path)

texts = []

for r in results:                 # each r is OCRResult
    data = r.json                 # dict with top-level key "res"
    res = data.get("res", {})
    for t in res.get("rec_texts", []):
        print(t)
        texts.append(t)

full_text = "\n".join(texts)
print(full_text)

with open("extracted_text.txt", "w", encoding="utf-8") as f:
    f.write(full_text)

print("Text extracted! " + full_text)
