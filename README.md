# Articles of Incorporation

A small Streamlit app for collecting article-of-incorporation images and converting them to Markdown.

## Setup

1. Install the Python dependency: `pip install -r requirements.txt`.
2. Install [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) and make sure the `tesseract` command is on your `PATH`.
3. Start the app from the repository root:

   ```sh
   streamlit run src/app.py
   ```

## Use

- In **Create articles**, select one or more local images or enter public HTTP(S) image URLs (one per line), then click **Create**. Images are stored in `raw_images/`.
- In **Convert to Markdown**, select stored images and click **Convert to Markdown**. OCR text is written to `readable_documents/` as `.md` files.
- The app supports BMP, GIF, JPEG, PNG, TIFF, and WebP images up to 25 MB each. URL redirects and non-public hosts are rejected.

Run tests with `python -m unittest discover -s tests`.