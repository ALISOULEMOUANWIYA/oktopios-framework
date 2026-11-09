"""
Tests e2e de l'API REST auto (Rest) et de l'autorisation par rôle
(requireRole), servis en HTTP réel — examples/rest_api.okp.
"""
import http.client
import json
import os
import socket
import subprocess
import sys
import time

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(REPO_ROOT, "examples", "rest_api.okp")


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
        pytest.skip("rest_api.okp introuvable")
    port = _free_port()
    db = os.path.join(REPO_ROOT, "rest_api.db")
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
            c.request("GET", "/api/produits")
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


def _req(port, method, path, body=None, cookie=None):
    c = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    headers = {}
    if cookie:
        headers["Cookie"] = cookie
    c.request(method, path, body=body, headers=headers)
    r = c.getresponse()
    data = r.read().decode("utf-8", "replace")
    status, setcookie = r.status, r.getheader("Set-Cookie")
    c.close()
    return status, data, setcookie


def test_rest_list_is_json(server):
    st, body, _ = _req(server, "GET", "/api/produits")
    assert st == 200
    items = json.loads(body)
    assert isinstance(items, list)
    assert items[0]["nom"] == "Stylo"
    assert "categorie" not in items[0]        # relation non incluse par défaut


def test_rest_include_relation(server):
    st, body, _ = _req(server, "GET", "/api/produits/1?include=categorie")
    assert st == 200
    one = json.loads(body)
    assert one["categorie"]["nom"] == "Papeterie"   # relation incluse


def test_rest_pagination_envelope(server):
    st, body, _ = _req(server, "GET", "/api/produits?page=1&perPage=1")
    assert st == 200
    env = json.loads(body)
    assert env["page"] == 1 and env["total"] >= 1
    assert isinstance(env["data"], list) and len(env["data"]) == 1


def test_rest_get_one_and_404(server):
    st, body, _ = _req(server, "GET", "/api/produits/1")
    assert st == 200 and json.loads(body)["nom"] == "Stylo"
    st2, _, _ = _req(server, "GET", "/api/produits/999")
    assert st2 == 404


def test_rest_post_validation_422(server):
    st, body, _ = _req(server, "POST", "/api/produits",
                       body='{"nom": "x", "prix": 1}')   # nom trop court (@MinLength 2)
    assert st == 422
    assert "erreurs" in json.loads(body)


def test_rest_post_put_delete(server):
    st, body, _ = _req(server, "POST", "/api/produits",
                       body='{"nom": "Cahier", "prix": 3}')
    assert st == 201
    created = json.loads(body)
    pid = created["id"]
    assert created["nom"] == "Cahier" and pid >= 2
    # PUT met à jour
    stp, bodyp, _ = _req(server, "PUT", "/api/produits/%d" % pid,
                         body='{"nom": "Cahier A4", "prix": 4}')
    assert stp == 200 and json.loads(bodyp)["nom"] == "Cahier A4"
    # DELETE supprime
    std, _, _ = _req(server, "DELETE", "/api/produits/%d" % pid)
    assert std == 200
    stg, _, _ = _req(server, "GET", "/api/produits/%d" % pid)
    assert stg == 404


def test_role_guard(server):
    # anonyme -> 401
    st, _, _ = _req(server, "GET", "/admin/stats")
    assert st == 401
    # connecté admin -> 200
    _, _, setcookie = _req(server, "GET", "/login?user=admin&pw=secret")
    cookie = setcookie.split(";")[0]
    st2, body2, _ = _req(server, "GET", "/admin/stats", cookie=cookie)
    assert st2 == 200 and "Zone admin" in body2
