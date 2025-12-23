import argparse
import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

def clean_html_response(text: str) -> str:
    """
    Extract a clean HTML document from a model response.

    Handles common cases:
    - Markdown fenced blocks like ```html ... ```
    - Preface/explanations before the HTML
    - Trailing commentary after </html>
    """
    if not text:
        return text

    s = text.strip()

    # Strip markdown fences if present
    if "```" in s:
        # Prefer ```html fenced blocks
        lower = s.lower()
        if "```html" in lower:
            start = lower.find("```html")
            start = s.find("\n", start)  # after the ```html line
            if start != -1:
                start += 1
                end = s.find("```", start)
                if end != -1:
                    s = s[start:end].strip()
        else:
            # Generic fenced block: take the first fenced block content
            first = s.find("```")
            if first != -1:
                start = s.find("\n", first)
                if start != -1:
                    start += 1
                    end = s.find("```", start)
                    if end != -1:
                        s = s[start:end].strip()

    lower = s.lower()
    # Find start of HTML doc
    start_idx = -1
    if "<!doctype" in lower:
        start_idx = lower.find("<!doctype")
    elif "<html" in lower:
        start_idx = lower.find("<html")

    if start_idx != -1:
        s2 = s[start_idx:]
        lower2 = s2.lower()
        end_idx = lower2.rfind("</html>")
        if end_idx != -1:
            s2 = s2[: end_idx + len("</html>")].strip()
        return s2

    return s

def make_client() -> OpenAI:
    load_dotenv()
    api_key = os.getenv("NOVITA_API_KEY")
    if not api_key:
        raise RuntimeError(
            "NOVITA_API_KEY not found. Create a .env file with:\n"
            "  NOVITA_API_KEY=your_key_here\n"
            "Or set it in your terminal session before running."
        )

    # Novita OpenAI-compatible base URL
    return OpenAI(api_key=api_key, base_url="https://api.novita.ai/openai")

def read_extracted_text(path: str = "extracted_text.txt") -> str:
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} not found. Run extract.py first.")
    # Prefer utf-8-sig so files saved for Windows Notepad (with BOM) load cleanly.
    for enc in ("utf-8-sig", "utf-8"):
        try:
            with open(path, "r", encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    # Last resort: surface a clear error
    raise UnicodeDecodeError("utf-8", b"", 0, 1, "Could not decode extracted text as UTF-8.")

def generate_html(*, input_path: str, output_path: str, model: str) -> str:
    client = make_client()
    text = read_extracted_text(input_path)

    prompt = (
        "Convert the following Nepali political document text into a single, complete, mobile-friendly HTML5 explainer website.\n"
        "Requirements:\n"
        "- Return ONLY the HTML (start with <!DOCTYPE html> or <html> and end with </html>).\n"
        "- Do NOT include markdown fences like ```html.\n"
        "- Do NOT include any explanation, notes, or extra text before/after the HTML.\n"
        "- Include inline CSS in a <style> tag.\n"
        "- Create a mobile-friendly, responsive design optimized for small screens.\n"
        "- Structure the content with:\n"
        "  * A clear summary section at the top\n"
        "  * Key points highlighted in lists\n"
        "  * Equality and representation sections clearly marked and emphasized\n"
        "  * Clean headings, paragraphs, and organized sections\n"
        "- Use professional styling with good readability for Nepali text.\n"
        "- Ensure the layout works well on mobile devices.\n\n"
        f"{text}"
    )

    print("Calling ERNIE via Novita chat.completions...")

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an expert web designer."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=4000,
        temperature=0.7,
    )

    raw = resp.choices[0].message.content or ""
    html = clean_html_response(raw)

    with open(output_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)

    print(f"HTML generated and saved to {output_path} (length={len(html)} characters)")
    return html

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="dastabej-to-Site: Generate index.html from extracted_text.txt via ERNIE (Novita).")
    parser.add_argument("--in", dest="input_path", default="extracted_text.txt", help="Input text file path")
    parser.add_argument("--out", dest="output_path", default="index.html", help="Output HTML file path")
    parser.add_argument("--model", default="baidu/ernie-4.5-vl-28b-a3b", help="Model name")
    parser.add_argument(
        "--pause",
        action="store_true",
        help="Pause before exit (useful when double-clicking on Windows).",
    )
    args = parser.parse_args()

    try:
        generate_html(input_path=args.input_path, output_path=args.output_path, model=args.model)
    except Exception as e:
        print("\nERROR:", e, file=sys.stderr)
        if args.pause:
            input("\nPress Enter to exit...")
        raise
    else:
        if args.pause:
            input("\nDone. Press Enter to exit...")
