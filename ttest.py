from paddleocr import PaddleOCRVL

pipeline = PaddleOCRVL()  # uses PaddleOCR-VL-0.9B[web:27]

image_path = r"C:\Users\ACER\Music\ernie\ernie-web-builder\sample.jpg"  # change this to your image

output = pipeline.predict(image_path)  # list of page results[web:27]

for res in output:
    res.print()
    res.save_to_json(save_path="output_cpu")
    res.save_to_markdown(save_path="output_cpu")
