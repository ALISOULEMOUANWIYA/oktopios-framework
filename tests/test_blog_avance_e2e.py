"""
Tests e2e de l'exemple avancé (examples/blog_avance.okp) : relations
@ManyToOne, pagination et messages flash, servis en HTTP réel.
"""
import http.client
import os
import socket
import subprocess
import sys
import time

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(REPO_ROOT, "examples", "blog_avance.okp")


def _free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def _child_env():
    env = dict(os.environ)
    extra = [REPO_ROOT]
    parent = os.path.dirname(REPO_ROOT)
    for sib in ("version.0.0.1", "oktopios-orm"):
        d = os.path.join(parent, sib)
        if os.path.isdir(d):
            extra.append(d)
    env["PYTHONPATH"] = os.pathsep.join(extra + [env.get("PYTHONPATH", "")])
    env["PYTHONIOENCODING"] = "utf-8"
    return env


@pytest.fixture(scope="module")
def server():
    if not os.path.exists(APP):
        pytest.skip("blog_avance.okp introuvable")
    port = _free_port()
    db = os.path.join(REPO_ROOT, "blog_avance.db")
    env = _child_env()
    env["OKTOPIOS_PORT"] = str(port)
    proc = subprocess.Popen(
        [sys.executable, "-m", "vm.main", APP],
        cwd=REPO_ROOT, env=env,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    deadline = time.time() + 15
    ready = False
    while time.time() < deadline:
        if proc.poll() is not None:
            pytest.fail("serveur arrete au demarrage:\n" + proc.stdout.read().decode("utf-8", "replace"))
        try:
            c = http.client.HTTPConnection("127.0.0.1", port, timeout=1)
            c.request("GET", "/")
            c.getresponse().read()
            c.close()
            ready = True
            break
        except OSError:
            time.sleep(0.3)
    if not ready:
        proc.terminate()
        pytest.fail("serveur non demarre a temps")
    yield port
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
    try:
        os.remove(db)
    except OSError:
        pass


def _get(port, path, cookie=None):
    c = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    headers = {"Cookie": cookie} if cookie else {}
    c.request("GET", path, headers=headers)
    r = c.getresponse()
    body = r.read().decode("utf-8", "replace")
    status, setcookie = r.status, r.getheader("Set-Cookie")
    c.close()
    return status, body, setcookie


def test_pagination_and_relation(server):
    _, p1, _ = _get(server, "/?page=1")
    assert "Article 1" in p1 and "Article 3" in p1
    assert "Article 4" not in p1           # 3 par page
    assert "Awa" in p1                      # relation @ManyToOne affichée
    assert "Page 1 / 2" in p1 and "Suivant" in p1
    _, p2, _ = _get(server, "/?page=2")
    assert "Article 4" in p2 and "Article 5" in p2
    assert "Precedent" in p2


def test_detail_shows_author(server):
    _, body, _ = _get(server, "/articles/1")
    assert "Par Awa" in body


def test_flash_after_create_is_one_shot(server):
    _, _, setcookie = _get(server, "/login?user=admin&pw=admin123")
    cookie = setcookie.split(";")[0]
    st, _, _ = _get(server, "/admin/create?titre=Nouveau&contenu=Frais", cookie=cookie)
    # redirection après création
    assert st in (301, 302)
    _, first, _ = _get(server, "/?page=1", cookie=cookie)
    assert "flash-success" in first and "Nouveau" in first
    _, second, _ = _get(server, "/?page=1", cookie=cookie)
    assert "flash-success" not in second   # message flash consommé
