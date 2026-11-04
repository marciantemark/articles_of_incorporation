# Current State

- `src/app.py` provides a Streamlit interface to upload images or fetch images from public HTTP(S) URLs.
- Images are stored under `raw_images/`.
- The app converts selected images to Markdown in `readable_documents/` using the local Tesseract OCR executable.
- See `README.md` for setup and usage instructions.
