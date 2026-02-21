import argparse
import os
import sys
from pathlib import Path
from typing import Iterable

MAX_CONTEXT_CHARS = 120_000


def load_env_file(env_path: str = ".env") -> None:
    """Best-effort .env loading without hard dependency at import time."""
    try:
        from dotenv import load_dotenv  # type: ignore
    except ImportError:
        return
    load_dotenv(env_path)


def extract_pdf_text(pdf_path: Path) -> str:
    """Extract text from all pages of a PDF file."""
    if not pdf_path.exists() or not pdf_path.is_file():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    from pypdf import PdfReader

    reader = PdfReader(str(pdf_path))
    all_text: list[str] = []
    for idx, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            all_text.append(f"--- Page {idx} ---\n{text}")

    combined = "\n\n".join(all_text).strip()
    if not combined:
        raise ValueError("Could not extract any text from the PDF.")
    return combined


def chunk_text(text: str, size: int = MAX_CONTEXT_CHARS) -> Iterable[str]:
    """Yield context-safe chunks for long documents."""
    for i in range(0, len(text), size):
        yield text[i : i + size]


def build_prompt(context: str, question: str) -> str:
    return (
        "You are a careful assistant. Use ONLY the provided PDF context to answer. "
        "If the answer is not present, explicitly say: 'I could not find that in the PDF.'\n\n"
        f"PDF CONTEXT:\n{context}\n\n"
        f"QUESTION: {question}\n"
        "ANSWER:"
    )


def ask_gemini(pdf_text: str, question: str, model_name: str = "gemini-1.5-flash") -> str:
    """Ask Gemini a question using extracted PDF text as context."""
    import google.generativeai as genai

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY is not set. Configure it in env or .env.")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)

    responses: list[str] = []
    for chunk in chunk_text(pdf_text, MAX_CONTEXT_CHARS):
        prompt = build_prompt(chunk, question)
        result = model.generate_content(prompt)
        text = (result.text or "").strip()
        if text:
            responses.append(text)

    if not responses:
        raise RuntimeError("Gemini returned an empty response.")

    if len(responses) == 1:
        return responses[0]

    summary_prompt = (
        "You are given multiple partial answers extracted from different PDF chunks. "
        "Merge them into one concise final answer. If conflicting, prefer overlap across chunks.\n\n"
        + "\n\n".join(f"Partial answer {i+1}:\n{r}" for i, r in enumerate(responses))
    )
    final = model.generate_content(summary_prompt)
    return (final.text or "").strip() or "\n\n".join(responses)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read a PDF and answer a question using Google Gemini 1.5."
    )
    parser.add_argument("--pdf", required=True, help="Path to the PDF file")
    parser.add_argument("--question", required=True, help="Question to answer from the PDF")
    parser.add_argument(
        "--model",
        default="gemini-1.5-flash",
        help="Gemini model name (default: gemini-1.5-flash)",
    )
    parser.add_argument(
        "--save-answer",
        help="Optional path to save answer as a text file",
    )
    parser.add_argument(
        "--env-file",
        default=".env",
        help="Optional .env file path (default: .env)",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    load_env_file(args.env_file)

    try:
        pdf_text = extract_pdf_text(Path(args.pdf))
        answer = ask_gemini(pdf_text, args.question, args.model)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print("\n=== Question ===")
    print(args.question)
    print("\n=== Answer ===")
    print(answer)

    if args.save_answer:
        out = Path(args.save_answer)
        out.write_text(answer + "\n", encoding="utf-8")
        print(f"\nSaved answer to: {out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
