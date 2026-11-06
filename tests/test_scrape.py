import json
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


def test_encoding_falls_back_to_iso_8859_1_without_meta(tmp_path):
    html_file = tmp_path / "latin1.html"
    html_file.write_bytes("<h1>Caffè</h1>".encode("iso-8859-1"))

    result = run_scrape(str(html_file), "-e", "string(//h1)")

    assert result.returncode == 0
    assert result.stdout == "Caffè\n"


def test_encoding_windows_1252_without_meta(tmp_path):
    html_file = tmp_path / "cp1252.html"
    html_file.write_bytes("<h1>Caffè € ’</h1>".encode("cp1252"))

    result = run_scrape(str(html_file), "-e", "string(//h1)")

    assert result.returncode == 0
    assert result.stdout == "Caffè € ’\n"


def test_encoding_bytes_undefined_in_windows_1252_fall_back_to_iso_8859_1(tmp_path):
    html_file = tmp_path / "undefined.html"
    html_file.write_bytes(b"<h1>Caff\xe8 \x81</h1>")

    result = run_scrape(str(html_file), "-e", "string(//h1)")

    assert result.returncode == 0
    assert result.stdout.startswith("Caffè")


def test_encoding_utf8_without_meta_is_not_converted(tmp_path):
    html_file = tmp_path / "utf8.html"
    html_file.write_bytes("<h1>Caffè €</h1>".encode("utf-8"))

    result = run_scrape(str(html_file), "-e", "string(//h1)")

    assert result.stdout == "Caffè €\n"


def test_rawinput_keeps_the_encoding_declared_by_the_xml(tmp_path):
    xml_file = tmp_path / "latin1.xml"
    xml_file.write_bytes('<?xml version="1.0" encoding="iso-8859-1"?><a>Caffè</a>'.encode("iso-8859-1"))

    result = run_scrape(str(xml_file), "-r", "-e", "string(//a)")

    assert result.returncode == 0
    assert result.stdout == "Caffè\n"


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


def test_rawinput_malformed_xml_reports_xml_error():
    result = run_scrape("-r", "-e", "//a", input_data="<root><a></root>")
    assert result.returncode == 1
    assert "Error parsing XML: " in result.stderr


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
    assert "Error: No input received from stdin" in result.stderr


def test_missing_file_returns_error():
    result = run_scrape("resources/this-file-does-not-exist.html", "-e", "//p")

    assert result.returncode == 1
    assert "was not found" in result.stderr


def test_missing_expression_without_text_returns_error():
    result = run_scrape(str(TEST_HTML))

    assert result.returncode == 1
    assert "no expression specified" in result.stderr


def test_incorrect_eb_order_exits_with_specific_message():
    result = run_scrape("-eb")

    assert result.returncode == 1
    assert "use -be not -eb" in result.stderr


def test_incorrect_ej_order_exits_with_specific_message():
    result = run_scrape("-ej")

    assert result.returncode == 1
    assert "use -je not -ej" in result.stderr


def test_order_checks_ignore_filenames_and_selectors(tmp_path):
    for name in ("page-eb.html", "page-ej.html"):
        html_file = tmp_path / name
        html_file.write_text("<h1>ok</h1>", encoding="utf-8")
        result = run_scrape(str(html_file), "-e", "h1")
        assert result.returncode == 0, result.stderr
        assert "ok" in result.stdout

    for selector in (".page-ejected", ".page-ebook"):
        result = run_scrape("-e", selector, input_data='<p class="x">ok</p>')
        assert "use -" not in result.stderr


def test_invalid_xpath_reports_clean_error():
    result = run_scrape("-e", "//[bad", input_data="<p>x</p>")

    assert result.returncode == 1
    assert "Error: invalid XPath" in result.stderr
    assert "Traceback" not in result.stderr


def test_unreadable_input_reports_clean_error(tmp_path):
    result = run_scrape("-e", "h1", str(tmp_path))

    assert result.returncode == 1
    assert "Error: cannot read" in result.stderr
    assert "Traceback" not in result.stderr


def test_help_documents_the_contract_for_agents():
    result = run_scrape("--help")

    assert result.returncode == 0
    for section in ("output:", "exit codes:", "notes:", "examples:", "--json-array"):
        assert section in result.stdout


def test_exit_codes_match_help():
    html = "<h1>x</h1>"

    no_match = run_scrape("-e", "//nulla", input_data=html)
    assert (no_match.returncode, no_match.stdout) == (0, "")

    not_found = run_scrape("-x", "-e", "//nulla", input_data=html)
    assert not_found.returncode == 1
    assert "Error" not in not_found.stderr

    assert run_scrape("--bogus", input_data=html).returncode == 2

    first_only = run_scrape("-x", "-e", "//nulla", "-e", "//h1", input_data=html)
    assert first_only.returncode == 1


def test_invalid_css_selector_fails_conversion():
    result = run_scrape(str(TEST_HTML), "-e", "div[")

    assert result.returncode == 1
    assert "Error converting CSS selector to XPath" in result.stderr


def test_json_flag_produces_valid_json_for_single_element():
    result = run_scrape(str(TEST_HTML), "-je", "a.external-link")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    a = payload["html"]["body"]["a"]
    assert a["@href"] == "https://example.com"
    assert a["@class"] == "external-link"
    assert a["#text"] == "Example Link"


def test_json_flag_produces_array_for_multiple_elements():
    result = run_scrape(str(TEST_HTML), "-je", "table.data-table td")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    tds = payload["html"]["body"]["td"]
    assert isinstance(tds, list)
    assert "Italy" in tds
    assert "Rome" in tds


def test_json_flag_works_without_b_flag():
    only_j = run_scrape(str(TEST_HTML), "-j", "-e", "a.external-link")
    with_bj = run_scrape(str(TEST_HTML), "-bj", "-e", "a.external-link")

    assert only_j.returncode == 0
    assert with_bj.returncode == 0
    assert only_j.stdout == with_bj.stdout


def test_json_flag_conflicts_with_text_check_existence_argument():
    jt = run_scrape(str(TEST_HTML), "-j", "-t")
    assert jt.returncode == 1
    assert "mutually exclusive" in jt.stderr

    jx = run_scrape(str(TEST_HTML), "-j", "-e", "//h1", "-x")
    assert jx.returncode == 1
    assert "mutually exclusive" in jx.stderr

    ja = run_scrape(str(TEST_HTML), "-j", "-e", "//a", "-a", "href")
    assert ja.returncode == 1
    assert "cannot be combined" in ja.stderr


def test_json_flag_handles_string_results_with_special_characters():
    html = '<a href="x?a=1&amp;b=2">AT&amp;T &lt;b&gt;</a>'

    attr = run_scrape("-je", "//a/@href", input_data=html)
    assert attr.returncode == 0, attr.stderr
    assert json.loads(attr.stdout)["html"]["body"] == "x?a=1&b=2"

    text = run_scrape("-je", "//a/text()", input_data=html)
    assert text.returncode == 0, text.stderr
    assert json.loads(text.stdout)["html"]["body"] == "AT&T <b>"


def test_json_flag_returns_array_for_multiple_string_results():
    html = '<a href="x?a=1&amp;b=2">uno</a> <a href="y">due</a>'

    attrs = run_scrape("-je", "//a/@href", input_data=html)
    assert attrs.returncode == 0, attrs.stderr
    assert json.loads(attrs.stdout)["html"]["body"] == ["x?a=1&b=2", "y"]

    # Whitespace-only text nodes are not results
    texts = run_scrape("-je", "//body//text()", input_data=html)
    assert json.loads(texts.stdout)["html"]["body"] == ["uno", "due"]


def test_json_flag_mixed_elements_and_strings_still_converts():
    result = run_scrape("-je", "//a | //a/@href", input_data='<a href="x&amp;y">uno</a>')

    assert result.returncode == 0, result.stderr
    body = json.loads(result.stdout)["html"]["body"]
    assert body["a"]["#text"] == "uno"
    assert body["#text"] == "x&y"


SCALAR_HTML = "<h1>Ciao</h1><a>1</a><a>2</a>"


def test_xpath_functions_return_a_single_value():
    cases = {
        "string(//h1)": "Ciao\n",
        "count(//a)": "2\n",
        "boolean(//a)": "true\n",
        "boolean(//nulla)": "false\n",
        "string(//nulla)": "",
    }
    for expression, expected in cases.items():
        result = run_scrape("-e", expression, input_data=SCALAR_HTML)
        assert result.returncode == 0, result.stderr
        assert result.stdout == expected, expression


def test_check_existence_follows_xpath_function_value():
    for expression, expected in {
        "string(//h1)": 0,
        "string(//nulla)": 1,
        "count(//a)": 0,
        "count(//nulla)": 1,
        "boolean(//a)": 0,
        "boolean(//nulla)": 1,
    }.items():
        result = run_scrape("-x", "-e", expression, input_data=SCALAR_HTML)
        assert result.returncode == expected, expression


def test_json_flag_with_xpath_functions():
    for expression, expected in {"string(//h1)": "Ciao", "count(//a)": "2"}.items():
        result = run_scrape("-je", expression, input_data=SCALAR_HTML)
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout)["html"]["body"] == expected


def test_json_flag_text_results_work_on_test_file():
    result = run_scrape(str(TEST_HTML), "-je", "//p/text()")

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["html"]["body"]


def test_json_flag_reports_clean_error_on_non_xml_attribute_name():
    result = run_scrape("-je", "#v", input_data='<div id="v" @click="go">x</div>')

    assert result.returncode == 1
    assert "Error:" in result.stderr
    assert "Traceback" not in result.stderr
    assert result.stdout == ""


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


TAIL_HTML = '<p>Prima <a href="/x">Link</a> dopo.</p>'
ARRAY_HTML = (
    '<html><body><!-- c --><p class="a">uno</p><p class="a">due</p>'
    '<a href="x">l</a><a href="y">m</a><b>tre</b></body></html>'
)


def test_text_after_element_stays_out_of_html_output():
    result = run_scrape("-e", "//a", input_data=TAIL_HTML)
    assert result.stdout.strip() == '<a href="/x">Link</a>'


def test_text_after_element_stays_out_of_body_output():
    result = run_scrape("-be", "//a", input_data=TAIL_HTML)
    assert "dopo" not in result.stdout


def test_text_after_element_stays_out_of_json_output():
    result = run_scrape("-je", "//a", input_data=TAIL_HTML)
    assert json.loads(result.stdout) == {"html": {"body": {"a": {"@href": "/x", "#text": "Link"}}}}


def json_array(*expressions, input_data=ARRAY_HTML):
    args = ["--json-array"]
    for expression in expressions:
        args += ["-e", expression]
    result = run_scrape(*args, input_data=input_data)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_json_array_no_results():
    assert json_array("p.none") == []


def test_json_array_one_result():
    assert json_array("b") == [{"b": "tre"}]


def test_json_array_several_results():
    assert json_array("//a/@href") == ["x", "y"]
    assert json_array("p") == [
        {"p": {"@class": "a", "#text": "uno"}},
        {"p": {"@class": "a", "#text": "due"}},
    ]


def test_json_array_keeps_the_order_of_the_expressions():
    assert json_array("//a/@href", "b") == ["x", "y", {"b": "tre"}]
    assert json_array("b", "//a/@href") == [{"b": "tre"}, "x", "y"]


def test_json_array_mixed_expressions_keep_order_and_forms():
    assert json_array("b", "//a/@href", "count(//p)") == [{"b": "tre"}, "x", "y", "2"]


def test_json_array_element_item():
    assert json_array("a")[0] == {"a": {"@href": "x", "#text": "l"}}


def test_json_array_leaves_out_text_after_element():
    assert json_array("b", input_data="<p>a <b>x</b> coda</p>") == [{"b": "x"}]


def test_json_array_xpath_functions():
    assert json_array("count(//p)") == ["2"]
    assert json_array("string(//none)") == []


def test_json_array_skips_comments():
    assert json_array("//comment()") == []


def test_json_array_rejects_conflicting_flags():
    for flags in (["-t"], ["-x"], ["-a", "href"]):
        result = run_scrape("--json-array", *flags, "-e", "a", input_data=ARRAY_HTML)
        assert result.returncode == 1
        assert "Error: --json-array " in result.stderr


def test_json_array_reports_clean_error_on_non_xml_attribute_name():
    result = run_scrape("--json-array", "-e", "a", input_data='<a @click="x">l</a>')
    assert result.returncode == 1
    assert result.stdout == ""
    assert "Error:" in result.stderr
    assert "Traceback" not in result.stderr
    assert "not supported by --json-array" in result.stderr


def test_json_array_conflict_does_not_change_json_messages():
    result = run_scrape("-j", "-t", "-e", "a", input_data=ARRAY_HTML)
    assert "Error: --json and --text" in result.stderr


def test_html_input_with_no_elements_reports_clean_error():
    for html in (" ", "<!-- c -->", '<?xml version="1.0"?>'):
        for flags in (["-e", "//a"], ["-t"], ["-j", "-e", "//a"], ["--json-array", "-e", "//a"]):
            result = run_scrape(*flags, input_data=html)
            assert result.returncode == 1
            assert result.stdout == ""
            assert "Error parsing HTML: no elements found" in result.stderr
            assert "Traceback" not in result.stderr
