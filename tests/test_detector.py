"""Tests for the Detector agent tool."""
import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.detector.tools import load_manga_page


def test_load_manga_page_missing_file():
    with pytest.raises(FileNotFoundError):
        load_manga_page("nonexistent.jpg")


def test_load_manga_page_valid(tmp_path):
    from PIL import Image
    img = Image.new("RGB", (800, 1200), color=(255, 255, 255))
    path = str(tmp_path / "test_page.jpg")
    img.save(path)

    result = load_manga_page(path)
    assert result["width"] <= 1500
    assert result["height"] <= 1500
    assert result["format"] == "jpeg"
    assert len(result["image_base64"]) > 0
