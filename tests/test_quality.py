"""Tests for the Quality Checker agent tool."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.quality.tools import create_quality_report


def test_quality_report_pass():
    report = create_quality_report(
        manga_title="Dragon Spirit",
        chapter=1,
        page=1,
        translation_accuracy=90,
        text_completeness=95,
        visual_quality=85,
        consistency=88,
        readability=92,
    )
    assert report["status"] == "pass"
    assert report["scores"]["overall"] == 90.0
    assert "report_id" in report


def test_quality_report_needs_review():
    report = create_quality_report(
        manga_title="Dragon Spirit",
        chapter=1,
        page=2,
        translation_accuracy=60,
        text_completeness=65,
        visual_quality=55,
        consistency=70,
        readability=68,
        issues=["Missing bubble R003"],
    )
    assert report["status"] == "needs_review"
    assert report["issues"] == ["Missing bubble R003"]
