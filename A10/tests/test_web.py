import os
import sys
import re
import socket
import subprocess
import time
from pathlib import Path
from urllib.parse import urlparse

import pytest
import requests
from playwright.sync_api import expect


A10_DIR = Path(__file__).resolve().parents[1]


def _is_port_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.25)
        return s.connect_ex((host, port)) == 0


def _wait_for_http_ok(url: str, timeout_s: int = 30) -> None:
    deadline = time.time() + timeout_s
    last_err = None
    while time.time() < deadline:
        try:
            r = requests.get(url, timeout=2)
            if r.status_code == 200:
                return
        except Exception as e:
            last_err = e
        time.sleep(0.25)
    raise RuntimeError(f"Server did not become ready at {url}. Last error: {last_err}")


@pytest.fixture(scope="session")
def server():
    host = "127.0.0.1"

    # pick a free port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, 0))
        port = s.getsockname()[1]

    base_url = f"http://{host}:{port}"

    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    env["PORT"] = str(port)

    print(f"[server] starting Flask on {base_url}", flush=True)

    proc = subprocess.Popen(
        [sys.executable, "app.py"],
        cwd=str(A10_DIR),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    try:
        try:
            _wait_for_http_ok(base_url, timeout_s=30)
            print("[server] ready", flush=True)
        except Exception:
            logs = ""
            if proc.stdout:
                try:
                    # non-blocking-ish: read what’s available
                    logs = proc.stdout.read()
                except Exception:
                    pass
            raise RuntimeError(f"Server failed to start.\n\nServer logs:\n{logs}")

        yield {"base_url": base_url}
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
   

def test_homepage_loads(server, page):
    base_url = server["base_url"]

    page.set_default_timeout(15_000)
    page.set_default_navigation_timeout(15_000)

    page.goto(base_url, wait_until="domcontentloaded", timeout=15_000)

    expect(page.locator("h1")).to_be_visible()
    expect(page.locator("input#smiles")).to_be_visible()
    expect(page.locator("button[type='submit']")).to_be_visible()


def test_lookup_renders_data_and_image(server, page):
    """
    End-to-end test:
    - Fill SMILES
    - Click Search (JS fetch -> Flask /api/lookup)
    - Assert:
      - Query info contains SMILES
      - Returned ChEMBL ID appears
      - At least one key field appears in table
      - Image src points to /static/renders/*.png and file exists on disk
    """
    base_url = server["base_url"]
    page.goto(base_url, wait_until="domcontentloaded")

    # Benzoic acid SMILES (course number 4 example from earlier tasks)
    smiles = "O=C(O)c1ccccc1"

    page.fill("input#smiles", smiles)
    page.click("button[type='submit']")

    # Rendering can take time (obabel + povray), so wait generously
    result_card = page.locator("#resultCard")
    expect(result_card).to_be_visible(timeout=90_000)

    # Check that the page shows the query SMILES
    expect(page.locator("#queryInfo")).to_contain_text(smiles)

    # Check that some ChEMBL ID appears (robust: CHEMBL followed by digits)
    query_text = page.locator("#queryInfo")
    expect(query_text).to_contain_text(re.compile(r"CHEMBL\d+"))

    # Check a few table keys exist
    expect(page.locator("table.table")).to_be_visible()
    expect(page.locator("table.table")).to_contain_text("Preferred name")
    expect(page.locator("table.table")).to_contain_text("Canonical SMILES")

    # Ensure the image has a src pointing to /static/renders/...png
    img = page.locator("#molImage")
    expect(img).to_have_attribute("src", re.compile(r"/static/renders/.*\.png"))

    src = img.get_attribute("src")
    assert src is not None

    # Remove cache-busting query (?v=...)
    parsed = urlparse(src)
    img_path = parsed.path  # /static/renders/<token>.png
    assert img_path.startswith("/static/renders/")
    assert img_path.endswith(".png")

    # Map URL path to local filesystem path
    local_png = A10_DIR / img_path.lstrip("/")
    assert local_png.exists(), f"Expected rendered PNG to exist: {local_png}"
    assert local_png.stat().st_size > 0, "Rendered PNG file is empty"


def test_invalid_smiles_shows_error(server, page):
    base_url = server["base_url"]
    page.goto(base_url, wait_until="domcontentloaded")

    # Intentionally invalid input (contains whitespace/newline)
    bad_smiles = "C C\n"

    page.fill("input#smiles", bad_smiles)
    page.click("button[type='submit']")

    # Should show an error on the same page, no navigation
    err = page.locator("#error")
    expect(err).to_be_visible(timeout=15_000)
    expect(err).to_contain_text(re.compile(r"Invalid SMILES|error", re.IGNORECASE))

    # Result card should remain hidden
    expect(page.locator("#resultCard")).to_be_hidden()
