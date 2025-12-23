# dastabej-to-Site

**dastabej-to-Site** – A tool that converts long Nepali political documents into mobile-friendly explainer websites with summaries, key points, and equality/representation sections highlighted.

## Overview

dastabej-to-Site transforms complex Nepali political documents (PDFs) into accessible, mobile-friendly web pages. The tool uses OCR (Optical Character Recognition) to extract text from documents and AI-powered generation to create structured, easy-to-read websites.

## Features

- 📄 **PDF Document Processing**: Extract text from Nepali political documents using PaddleOCR
- 🤖 **AI-Powered HTML Generation**: Convert extracted text into clean, mobile-friendly HTML using ERNIE AI
- 📱 **Mobile-Friendly Design**: Responsive layouts optimized for mobile devices
- ✨ **Structured Content**: Automatically generates summaries, key points, and highlights equality/representation sections
- 🌐 **Nepali Language Support**: Optimized for Devanagari script and Nepali language processing

## Workflow

1. **Extract Text** (`extract.py`): Uses PaddleOCR to extract text from PDF or image files
2. **Generate HTML** (`generate_html.py`): Converts extracted text into a complete HTML website using ERNIE AI

## Requirements

- Python 3.10+
- PaddleOCR
- OpenAI-compatible API (via Novita for ERNIE)
- pypdfium2 (for PDF processing)

## Setup

1. Install dependencies:
```bash
pip install paddleocr openai python-dotenv pypdfium2
```

2. Create a `.env` file with your API key:
```
NOVITA_API_KEY=your_key_here
```

## Usage

### Step 1: Extract Text from PDF

```bash
python extract.py sample.pdf --out extracted_text.txt --lang ne
```

Options:
- `--lang`: Language code (`ne` for Nepali, `en` for English)
- `--out`: Output text file path
- `--pdf-scale`: Render scale for PDF pages (higher = sharper, slower)

### Step 2: Generate HTML Website

```bash
python generate_html.py --in extracted_text.txt --out index.html
```

Options:
- `--in`: Input text file path (default: `extracted_text.txt`)
- `--out`: Output HTML file path (default: `index.html`)
- `--model`: ERNIE model name (default: `baidu/ernie-4.5-vl-28b-a3b`)

## Project Structure

```
.
├── extract.py              # Text extraction from PDFs/images
├── generate_html.py        # HTML generation from extracted text
├── index.html              # Generated output HTML file
├── extracted_text.txt      # Extracted text (intermediate)
├── sample.pdf              # Sample input document
└── output_cpu/             # Output directory for OCR results
```

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]

