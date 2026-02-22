import subprocess
import sys
import threading
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer

ROOT = Path(__file__).resolve().parents[1]
TEST_HTML = ROOT / "resources" / "test.html"
sys.path.insert(0, str(ROOT))

from scrape_cli.scrape import is_xpath


def run_scrape(*args, input_data=None):
    cmd = [sys.executable, "-m", "scrape_cli.scrape", *args]
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=ROOT,
        input=input_data,
    )


def run_test_server(html_bytes):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html_bytes)

        def log_message(self, format, *args):
            return

    server = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def test_is_xpath_true_patterns():
    candidates = [
        "//div",
        "/html/body/div",
        "(//div)[1]",
        "//a/@href",
        "//li[2]",
        "ancestor::div",
        "descendant::span",
        "//p/text()",
    ]

    for expression in candidates:
        assert is_xpath(expression) is True


def test_is_xpath_false_css_patterns():
    candidates = [
        "div.content > a.link",
        "a[href*='/about']",
        "input[type='email']",
        "ul.items-list li:first-child",
        "div.class1.class2",
    ]

    for expression in candidates:
        assert is_xpath(expression) is False


def test_xpath_parentheses_extracts_first_match():
    result = run_scrape(str(TEST_HTML), "-e", "(//ul[@class='items-list']/li)[1]", "-t")

    assert result.returncode == 0
    assert result.stdout.strip() == "First item"


def test_css_attribute_selector_is_not_misclassified_as_xpath():
    result = run_scrape(str(TEST_HTML), "-e", ".resource-links a[href*='github.com']", "-t")

    assert result.returncode == 0
    assert result.stdout.strip() == "GitHub Repository"


def test_check_existence_true_and_false():
    found = run_scrape(str(TEST_HTML), "-e", "//h1", "--check-existence")
    missing = run_scrape(str(TEST_HTML), "-e", "//this-node-does-not-exist", "--check-existence")

    assert found.returncode == 0
    assert missing.returncode == 1


def test_encoding_meta_charset_iso_8859_1(tmp_path):
    html = """<!doctype html>
<html>
<head><meta charset=\"iso-8859-1\"></head>
<body><p>Perch\xe9</p></body>
</html>
""".encode("iso-8859-1")
    sample = tmp_path / "latin1.html"
    sample.write_bytes(html)

    result = run_scrape(str(sample), "-e", "//p/text()", "-t")

    assert result.returncode == 0
    assert result.stdout.strip() == "Perché"


def test_argument_extracts_attribute_value():
    result = run_scrape(str(TEST_HTML), "-e", "//a[@class='external-link']", "-a", "href")

    assert result.returncode == 0
    assert result.stdout.strip() == "https://example.com"


def test_body_flag_wraps_output_in_html_body():
    result = run_scrape(str(TEST_HTML), "-e", "//h1", "-b")

    assert result.returncode == 0
    assert result.stdout.startswith("<!DOCTYPE html>\n<html>\n<body>\n")
    assert result.stdout.strip().endswith("</body>\n</html>")
    assert "<h1 id=\"main-title\">Welcome to the Test Page</h1>" in result.stdout


def test_text_flag_without_expression_extracts_body_and_skips_script():
    result = run_scrape(str(TEST_HTML), "-t")

    assert result.returncode == 0
    assert "Welcome to the Test Page" in result.stdout
    assert "document.getElementById('dynamic-content')" not in result.stdout


def test_short_check_existence_flag_x():
    found = run_scrape(str(TEST_HTML), "-e", "//table", "-x")
    missing = run_scrape(str(TEST_HTML), "-e", "//definitely-not-here", "-x")

    assert found.returncode == 0
    assert missing.returncode == 1


def test_rawinput_parses_xml_without_html_parser():
    xml_data = "<root><item>one</item><item>two</item></root>"
    result = run_scrape("-e", "//item[2]/text()", "-r", input_data=xml_data)

    assert result.returncode == 0
    assert result.stdout.strip() == "two"


def test_stdin_input_works_when_no_html_argument():
    html_data = "<html><body><p>stdin-ok</p></body></html>"
    result = run_scrape("-e", "//p/text()", "-t", input_data=html_data)

    assert result.returncode == 0
    assert result.stdout.strip() == "stdin-ok"


def test_empty_stdin_returns_error():
    result = run_scrape("-e", "//p", input_data="")

    assert result.returncode == 1
    assert "Error: No input received from stdin" in result.stdout


def test_missing_file_returns_error():
    result = run_scrape("resources/this-file-does-not-exist.html", "-e", "//p")

    assert result.returncode == 1
    assert "was not found" in result.stdout


def test_missing_expression_without_text_returns_error():
    result = run_scrape(str(TEST_HTML))

    assert result.returncode == 1
    assert "you must provide at least one XPath query or CSS3 selector" in result.stderr


def test_incorrect_eb_order_exits_with_specific_message():
    result = run_scrape("-eb")

    assert result.returncode == 1
    assert "Please use -be instead of -eb." in result.stderr


def test_invalid_css_selector_fails_conversion():
    result = run_scrape(str(TEST_HTML), "-e", "div[")

    assert result.returncode == 1
    assert "Error converting CSS selector to XPath" in result.stdout


def test_url_input_downloads_and_extracts_text():
    html_bytes = TEST_HTML.read_bytes()
    server, thread = run_test_server(html_bytes)

    try:
        url = f"http://127.0.0.1:{server.server_address[1]}"
        result = run_scrape(url, "-e", "//h1/text()", "-t")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert result.returncode == 0
    assert result.stdout.strip() == "Welcome to the Test Page"
