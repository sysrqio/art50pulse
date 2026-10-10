from pathlib import Path

from art50pulse.audit import run_audit

ROOT = Path(__file__).resolve().parents[1]
HTML_BAD = ROOT / "testdata/html/chat_no_disclosure.html"
HTML_GOOD = ROOT / "testdata/html/chat_with_disclosure.html"
MEDIA = ROOT / "testdata/media/plain.png"


def test_clean_html_passes():
    report = run_audit(html_paths=[HTML_GOOD])
    assert report.ok


def test_chat_widget_without_disclosure_fails():
    report = run_audit(html_paths=[HTML_BAD])
    assert not report.ok
    assert any(v.code == "MISSING_CHATBOT_DISCLOSURE" for v in report.violations)


def test_c2pa_required_on_plain_media():
    report = run_audit(media_paths=[MEDIA], require_c2pa=True)
    assert not report.ok
    assert any(v.code == "MISSING_C2PA_MANIFEST" for v in report.violations)
