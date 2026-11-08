"""
Tests d'intégration end-to-end de l'app de référence (examples/blog_complet.okp).

Démarre réellement le serveur HTTP du blog (ORM + Auth + Vues + Formulaires +
Middleware) dans un sous-processus, puis exerce le parcours complet via HTTP :
liste, détail, 404, login + cookie, création protégée (401 sans session, 302
avec), validation (422).

Exécution :
    pip install oktopios oktopios-orm        # ou dépôts frères sur PYTHONPATH
    pytest                                   # depuis la racine de oktopios-framework

En monorepo de dev (dépôts côte à côte), les sources de `oktopios`
(../version.0.0.1) et `oktopios-orm` (../oktopios-orm) sont ajoutées
automatiquement au PYTHONPATH du sous-processus si elles existent.
"""
import http.client
import os
import socket
import subprocess
import sys
import time

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(REPO_ROOT, "examples", "blog_complet.okp")


def _free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def _child_env():
    """PYTHONPATH : ajoute les dépôts frères (dev) s'ils existent, sinon on
    compte sur les paquets installés (oktopios, oktopios-orm)."""
    env = dict(os.environ)
    extra = []
    parent = os.path.dirname(REPO_ROOT)
    for sibling in ("version.0.0.1", "oktopios-orm"):
        p = os.path.join(parent, sibling)
        if os.path.isdir(p):
            extra.append(p)
    extra.append(REPO_ROOT)  # pour `use "oktopios_framework/..."` si besoin
    if extra:
        env["PYTHONPATH"] = os.pathsep.join(extra + [env.get("PYTHONPATH", "")])
    env["PYTHONIOENCODING"] = "utf-8"
    return env


@pytest.fixture(scope="module")
def server():
    if not os.path.exists(APP):
        pytest.skip("exemple blog_complet.okp introuvable")

    port = _free_port()
    # Copie temporaire avec le port de test (l'exemple code 8000 en dur).
    src = open(APP, "r", encoding="utf-8").read().replace("8000", str(port))
    app_tmp = os.path.join(REPO_ROOT, "_blog_e2e_tmp.okp")
    db_tmp = os.path.join(REPO_ROOT, "blog_complet.db")
    with open(app_tmp, "w", encoding="utf-8") as f:
        f.write(src)

    proc = subprocess.Popen(
        [sys.executable, "-m", "vm.main", app_tmp],
        cwd=REPO_ROOT, env=_child_env(),
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    # Attendre que le serveur réponde (ou échouer avec le log du process).
    deadline = time.time() + 15
    ready = False
    while time.time() < deadline:
        if proc.poll() is not None:
            log = proc.stdout.read().decode("utf-8", "replace")
            pytest.fail("le serveur s'est arrete au demarrage:\n" + log)
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
        pytest.fail("le serveur n'a pas demarre a temps")

    yield port

    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
    for p in (app_tmp, db_tmp):
        try:
            os.remove(p)
        except OSError:
            pass


def _get(port, path, cookie=None, follow=False):
    c = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    headers = {"Cookie": cookie} if cookie else {}
    c.request("GET", path, headers=headers)
    r = c.getresponse()
    body = r.read().decode("utf-8", "replace")
    status = r.status
    location = r.getheader("Location")
    setcookie = r.getheader("Set-Cookie")
    c.close()
    return status, body, location, setcookie


def test_home_lists_seed_article(server):
    status, body, _, _ = _get(server, "/")
    assert status == 200
    assert "Bienvenue" in body
    assert "article(s)" in body


def test_create_requires_auth(server):
    status, _, _, _ = _get(server, "/admin/create?titre=Hack&contenu=xxx")
    assert status == 401


def test_login_sets_cookie(server):
    status, _, _, setcookie = _get(server, "/login?user=admin&pw=admin123")
    assert status == 200
    assert setcookie and "oktopios_session=" in setcookie


def test_full_create_flow_and_detail(server):
    # login -> cookie
    _, _, _, setcookie = _get(server, "/login?user=admin&pw=admin123")
    cookie = setcookie.split(";")[0]
    # création protégée -> redirection vers /articles/<id>
    status, _, location, _ = _get(
        server, "/admin/create?titre=MonArticle&contenu=Du%20contenu", cookie=cookie)
    assert status == 302
    assert "/articles/" in location
    # le détail de l'article créé s'affiche
    path = location.split("127.0.0.1:%d" % server)[-1] if "127.0.0.1" in location else location
    sdetail, bdetail, _, _ = _get(server, path)
    assert sdetail == 200
    assert "MonArticle" in bdetail
    assert "Du contenu" in bdetail


def test_validation_rejects_short_title(server):
    _, _, _, setcookie = _get(server, "/login?user=admin&pw=admin123")
    cookie = setcookie.split(";")[0]
    status, body, _, _ = _get(
        server, "/admin/create?titre=ab&contenu=xyz", cookie=cookie)
    assert status == 422
    assert "titre" in body


def test_unknown_article_404(server):
    status, _, _, _ = _get(server, "/articles/999999")
    assert status == 404
