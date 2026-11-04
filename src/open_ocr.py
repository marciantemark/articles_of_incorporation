import subprocess
from pathlib import Path


def extract_text(image_path: Path) -> str:
    try:
        result = subprocess.run(
            ["tesseract", str(image_path), "stdout"],
            check=True,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except FileNotFoundError as error:
        raise RuntimeError(
            "Tesseract OCR is not installed. Install Tesseract to convert images."
        ) from error
    except subprocess.TimeoutExpired as error:
        raise RuntimeError(f"OCR took too long for {image_path.name}.") from error
    except subprocess.CalledProcessError as error:
        detail = error.stderr.strip() or "Tesseract could not read this image."
        raise RuntimeError(detail) from error
    return result.stdout.strip()


def convert_to_markdown(image_path: Path, readable_directory: Path) -> Path:
    text = extract_text(image_path)
    readable_directory.mkdir(parents=True, exist_ok=True)
    markdown_path = readable_directory / f"{image_path.stem}.md"
    content = f"# {image_path.stem.replace('_', ' ')}\n\n"
    content += f"{text}\n" if text else "_No text was recognized in this image._\n"
    markdown_path.write_text(content, encoding="utf-8")
    return markdown_path
