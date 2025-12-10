from __future__ import annotations

from pathlib import Path
from typing import Dict

import requests

from config import DATA_URLS, RAW_DATA_DIR, RAW_FILENAMES


def _download_file(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=120) as response:
        response.raise_for_status()
        with destination.open("wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)


def download_data(force: bool = False) -> Dict[str, Path]:
    downloaded_paths: Dict[str, Path] = {}
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    for name, url in DATA_URLS.items():
        target_path = RAW_DATA_DIR / RAW_FILENAMES[name]
        if target_path.exists() and not force:
            downloaded_paths[name] = target_path
            continue

        _download_file(url, target_path)
        downloaded_paths[name] = target_path

    return downloaded_paths


if __name__ == "__main__":
    download_data(force=False)
