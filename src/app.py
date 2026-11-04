from pathlib import Path

import streamlit as st

from article_store import download_image, list_images, save_image
from open_ocr import convert_to_markdown

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
RAW_IMAGES = REPOSITORY_ROOT / "raw_images"
READABLE_DOCUMENTS = REPOSITORY_ROOT / "readable_documents"

st.set_page_config(page_title="Articles of Incorporation", page_icon="📄")
st.title("Articles of Incorporation")
st.write("Upload article images or provide image URLs, then convert them to Markdown.")

upload_tab, convert_tab = st.tabs(["Create articles", "Convert to Markdown"])

with upload_tab:
    uploaded_files = st.file_uploader(
        "Choose article images",
        type=["bmp", "gif", "jpg", "jpeg", "png", "tif", "tiff", "webp"],
        accept_multiple_files=True,
    )
    image_urls = st.text_area(
        "Image URLs (one HTTP or HTTPS URL per line)",
        help="URLs must point to publicly accessible images. Redirects are not followed.",
    )
    if st.button("Create", type="primary"):
        sources = [(uploaded.name, uploaded.getvalue()) for uploaded in uploaded_files]
        urls = [url.strip() for url in image_urls.splitlines() if url.strip()]
        if not sources and not urls:
            st.warning("Choose at least one image or enter an image URL.")
        else:
            saved = []
            failures = []
            for name, data in sources:
                try:
                    saved.append(save_image(data, name, RAW_IMAGES))
                except (OSError, ValueError) as error:
                    failures.append(f"{name}: {error}")
            for url in urls:
                try:
                    name, data = download_image(url)
                    saved.append(save_image(data, name, RAW_IMAGES))
                except (OSError, ValueError) as error:
                    failures.append(f"{url}: {error}")
            if saved:
                st.success(f"Saved {len(saved)} image(s) to raw_images.")
                st.write([path.name for path in saved])
            for failure in failures:
                st.error(failure)

with convert_tab:
    images = list_images(RAW_IMAGES)
    if not images:
        st.info("No images are available to convert yet.")
    else:
        selected_images = st.multiselect(
            "Select images to convert",
            images,
            format_func=lambda path: path.name,
            default=images,
        )
        if st.button("Convert to Markdown", type="primary"):
            converted = []
            failures = []
            for image in selected_images:
                try:
                    converted.append(convert_to_markdown(image, READABLE_DOCUMENTS))
                except (OSError, RuntimeError) as error:
                    failures.append(f"{image.name}: {error}")
            if converted:
                st.success(f"Created {len(converted)} Markdown document(s).")
                st.write([path.name for path in converted])
            for failure in failures:
                st.error(failure)
