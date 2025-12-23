import argparse
import os
import sys
from pathlib import Path

from paddleocr import PaddleOCR


def render_pdf_to_images(pdf_path: str, out_dir: str, *, scale: float = 3.0) -> list[str]:
    """
    Render a PDF into per-page PNGs and return their file paths.

    Requires: pypdfium2 (+ Pillow, typically pulled in).
    """
    try:
        import pypdfium2 as pdfium  # type: ignore
    except Exception as e:  # pragma: no cover
        raise RuntimeError(
            "PDF input requires 'pypdfium2'. Install it in your environment or run using the bundled venv."
        ) from e

    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    pdf = pdfium.PdfDocument(pdf_path)
    try:
        image_paths: list[str] = []
        for i in range(len(pdf)):
            page = pdf[i]
            # Scale controls effective DPI; higher improves OCR on small fonts.
            pil_image = page.render(scale=scale).to_pil()
            png_path = out_path / f"page_{i + 1:03d}.png"
            pil_image.save(png_path)
            image_paths.append(str(png_path))
        return image_paths
    finally:
        close = getattr(pdf, "close", None)
        if callable(close):
            close()


def extract_text(input_path: str, output_path: str, *, lang: str, pdf_scale: float) -> str:
    ocr = PaddleOCR(lang=lang, use_textline_orientation=True)

    inp = Path(input_path)
    if not inp.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # Decide what to OCR
    if inp.suffix.lower() == ".pdf":
        images = render_pdf_to_images(
            str(inp),
            out_dir=os.path.join("output_cpu", "pdf_pages"),
            scale=pdf_scale,
        )
    else:
        images = [str(inp)]

    texts: list[str] = []
    for idx, img_path in enumerate(images, start=1):
        results = ocr.predict(img_path)
        for r in results:  # each r is OCRResult
            data = r.json  # dict with top-level key "res"
            res = data.get("res", {})
            for t in res.get("rec_texts", []):
                texts.append(t)
        if len(images) > 1 and idx != len(images):
            texts.append("\n--- PAGE BREAK ---\n")

    full_text = "\n".join(texts)

    print(f"Text extracted! Extracted {len(full_text)} characters")
    return full_text


def main() -> None:
    # Prevent UnicodeEncodeError when printing Devanagari etc. on Windows consoles.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    # Speed up startup: skip model hoster connectivity check unless user overrides env var.
    os.environ.setdefault("DISABLE_MODEL_SOURCE_CHECK", "True")

    parser = argparse.ArgumentParser(description="dastabej-to-Site: Extract text from an image or PDF using PaddleOCR.")
    default_input = "sample.pdf" if Path("sample.pdf").exists() else "sample.jpg"
    parser.add_argument("input", nargs="?", default=default_input, help="Input file path (.jpg/.png/.pdf)")
    parser.add_argument("--out", default="extracted_text.txt", help="Output text file path")
    parser.add_argument(
        "--lang",
        default=None,
        help=(
            "OCR language code (examples: en, ne, hi). "
            "If omitted: PDFs default to 'ne' (Nepali/Devanagari), images default to 'en'."
        ),
    )
    parser.add_argument(
        "--pdf-scale",
        type=float,
        default=4.0,
        help="Render scale for PDF pages before OCR (higher = sharper, slower).",
    )
    parser.add_argument(
        "--encoding",
        default="utf-8-sig",
        help="Text file encoding for --out (recommended: utf-8-sig on Windows).",
    )
    args = parser.parse_args()

    inp = Path(args.input)
    if args.lang is None:
        args.lang = "ne" if inp.suffix.lower() == ".pdf" else "en"

    # Extract, then save using requested encoding.
    text = extract_text(args.input, args.out, lang=args.lang, pdf_scale=args.pdf_scale)
    with open(args.out, "w", encoding=args.encoding, newline="\n") as f:
        f.write(text)

    print(f"Saved to {args.out} (encoding={args.encoding}, lang={args.lang})")


if __name__ == "__main__":
    main()
