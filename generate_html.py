import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("NOVITA_API_KEY")
if not api_key:
    raise RuntimeError("NOVITA_API_KEY not found in .env")

# Novita OpenAI-compatible base URL
client = OpenAI(
    api_key=api_key,
    base_url="https://api.novita.ai/openai"
)

def read_extracted_text(path: str = "extracted_text.txt") -> str:
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} not found. Run extract.py first.")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def generate_html():
    text = read_extracted_text()

    prompt = (
        "Convert the following document text into a single, complete, "
        "beautiful, responsive HTML5 page with inline CSS. "
        "Use a clean professional layout, headings, paragraphs, and lists.\n\n"
        f"{text}"
    )

    print("Calling ERNIE via Novita chat.completions...")

    resp = client.chat.completions.create(
        model="baidu/ernie-4.5-vl-28b-a3b",
        messages=[
            {"role": "system", "content": "You are an expert web designer."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=4000,
        temperature=0.7,
    )

    html = resp.choices[0].message.content

    out_path = "index.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"HTML generated and saved to {out_path} (length={len(html)} characters)")

if __name__ == "__main__":
    generate_html()
