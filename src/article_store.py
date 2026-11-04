import ipaddress
import re
import socket
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

MAX_IMAGE_BYTES = 25 * 1024 * 1024
IMAGE_SIGNATURES = (
    (b"\x89PNG\r\n\x1a\n", ".png"),
    (b"\xff\xd8\xff", ".jpg"),
    (b"GIF87a", ".gif"),
    (b"GIF89a", ".gif"),
    (b"BM", ".bmp"),
    (b"II*\x00", ".tif"),
    (b"MM\x00*", ".tif"),
)


class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def image_extension(data: bytes) -> str:
    for signature, extension in IMAGE_SIGNATURES:
        if data.startswith(signature):
            return extension
    if len(data) >= 12 and data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return ".webp"
    raise ValueError("The selected file is not a supported image.")


def _safe_stem(filename: str) -> str:
    stem = Path(filename).stem
    stem = re.sub(r"[^A-Za-z0-9_-]+", "_", stem).strip("_-")
    return stem[:100] or "article"


def save_image(data: bytes, filename: str, directory: Path) -> Path:
    if not data:
        raise ValueError("The selected image is empty.")
    if len(data) > MAX_IMAGE_BYTES:
        raise ValueError("Images must be 25 MB or smaller.")

    extension = image_extension(data)
    directory.mkdir(parents=True, exist_ok=True)
    stem = _safe_stem(filename)
    for index in range(1000):
        suffix = "" if index == 0 else f"_{index}"
        destination = directory / f"{stem}{suffix}{extension}"
        try:
            with destination.open("xb") as image_file:
                image_file.write(data)
            return destination
        except FileExistsError:
            continue
    raise FileExistsError("Could not save the image because its name is already in use.")


def _validate_public_host(hostname: str) -> None:
    try:
        addresses = {ipaddress.ip_address(hostname)}
    except ValueError:
        try:
            addresses = {
                ipaddress.ip_address(result[4][0])
                for result in socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)
            }
        except (OSError, ValueError) as error:
            raise ValueError("The image URL host could not be resolved.") from error
    if not addresses or any(not address.is_global for address in addresses):
        raise ValueError("Image URLs must point to a public internet host.")


def download_image(url: str) -> tuple[str, bytes]:
    parsed_url = urllib.parse.urlparse(url)
    if parsed_url.scheme not in {"http", "https"} or not parsed_url.hostname:
        raise ValueError("Enter a valid HTTP or HTTPS image URL.")
    _validate_public_host(parsed_url.hostname)

    request = urllib.request.Request(url, headers={"User-Agent": "ArticlesOfIncorporation/1.0"})
    opener = urllib.request.build_opener(NoRedirectHandler)
    try:
        with opener.open(request, timeout=10) as response:
            data = response.read(MAX_IMAGE_BYTES + 1)
            filename = Path(urllib.parse.unquote(urllib.parse.urlparse(response.geturl()).path)).name
    except urllib.error.HTTPError as error:
        if 300 <= error.code < 400:
            raise ValueError("Image URL redirects are not supported.") from error
        raise ValueError(f"Could not download the image (HTTP {error.code}).") from error
    except OSError as error:
        raise ValueError("Could not download the image from that URL.") from error

    if not filename:
        filename = "article"
    if len(data) > MAX_IMAGE_BYTES:
        raise ValueError("Images must be 25 MB or smaller.")
    image_extension(data)
    return filename, data


def list_images(directory: Path) -> list[Path]:
    return sorted(
        (path for path in directory.iterdir() if path.is_file() and path.suffix.lower() in {
            ".bmp", ".gif", ".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp"
        }),
        key=lambda path: path.name.lower(),
    ) if directory.exists() else []
