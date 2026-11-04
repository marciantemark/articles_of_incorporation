import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.article_store import download_image, image_extension, list_images, save_image
from src.open_ocr import convert_to_markdown


class ArticleStoreTests(unittest.TestCase):
    def test_detects_supported_image_signatures(self):
        self.assertEqual(image_extension(b"\x89PNG\r\n\x1a\nimage"), ".png")
        self.assertEqual(image_extension(b"\xff\xd8\xffimage"), ".jpg")
        self.assertEqual(image_extension(b"RIFFxxxxWEBPimage"), ".webp")

    def test_rejects_non_images(self):
        with self.assertRaises(ValueError):
            image_extension(b"not an image")

    def test_rejects_non_http_and_private_image_urls(self):
        for url in ("file:///etc/passwd", "http://127.0.0.1/image.png"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                download_image(url)

    def test_saves_with_safe_unique_names_and_detected_extension(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            data = b"\x89PNG\r\n\x1a\nimage"

            first = save_image(data, "../../articles of incorporation.exe", directory)
            second = save_image(data, "../../articles of incorporation.exe", directory)

            self.assertEqual(first.name, "articles_of_incorporation.png")
            self.assertEqual(second.name, "articles_of_incorporation_1.png")
            self.assertEqual(first.read_bytes(), data)

    def test_lists_images_and_converts_ocr_text_to_markdown(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            raw_images = root / "raw_images"
            readable_documents = root / "readable_documents"
            image = save_image(b"\xff\xd8\xffimage", "articles.jpg", raw_images)
            (raw_images / "notes.txt").write_text("not an image", encoding="utf-8")

            self.assertEqual(list_images(raw_images), [image])
            with patch("src.open_ocr.extract_text", return_value="Company name"):
                markdown = convert_to_markdown(image, readable_documents)

            self.assertEqual(
                markdown.read_text(encoding="utf-8"),
                "# articles\n\nCompany name\n",
            )
            self.assertEqual(markdown.name, "articles_jpg.md")


if __name__ == "__main__":
    unittest.main()
