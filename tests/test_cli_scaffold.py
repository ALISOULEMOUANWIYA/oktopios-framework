"""
Tests du scaffolding CLI (`oktopios new` et `oktopios new --full`).

Vérifie que les générateurs produisent l'arborescence attendue et du contenu
cohérent (décorateurs, routes protégées, garde requireAuth…).
"""
import os

from oktopios_framework import cli


def _run(args, cwd, monkeypatch):
    monkeypatch.chdir(cwd)
    return cli.main(args)


def test_new_minimal(tmp_path, monkeypatch):
    rc = _run(["new", "app"], tmp_path, monkeypatch)
    assert rc == 0
    root = tmp_path / "app"
    for rel in ("main.okp", "controllers/home.okp", "templates/home.html",
                ".env.local", ".env.prod", "bin/migrate.okp"):
        assert (root / rel).exists(), rel


def test_new_full_structure(tmp_path, monkeypatch):
    rc = _run(["new", "--full", "blog"], tmp_path, monkeypatch)
    assert rc == 0
    root = tmp_path / "blog"
    expected = [
        "main.okp",
        "models/article.okp",
        "controllers/articles.okp",
        "controllers/auth.okp",
        "templates/layout.html",
        "templates/list.html",
        "templates/show.html",
        "bin/migrate.okp",
        ".env.local",
        ".env.prod",
        ".gitignore",
        "Dockerfile",
        ".dockerignore",
    ]
    for rel in expected:
        assert (root / rel).exists(), rel


def test_new_full_content(tmp_path, monkeypatch):
    _run(["new", "--full", "blog"], tmp_path, monkeypatch)
    root = tmp_path / "blog"

    model = (root / "models" / "article.okp").read_text(encoding="utf-8")
    assert '@Entity("articles")' in model
    assert "@Id" in model and "@NotNull" in model

    main = (root / "main.okp").read_text(encoding="utf-8")
    # nom de projet substitué, et pile complète câblée
    assert "blog" in main
    assert "requireAuth" in main            # route protégée
    assert 'use "oktopios_orm/orm.okp"' in main
    assert 'use "controllers/articles.okp"' in main

    ctrl = (root / "controllers" / "articles.okp").read_text(encoding="utf-8")
    assert "form.validate" in ctrl and "repo.save" in ctrl


def test_new_full_refuses_nonempty_dir(tmp_path, monkeypatch):
    (tmp_path / "blog").mkdir()
    (tmp_path / "blog" / "x.txt").write_text("deja la", encoding="utf-8")
    rc = _run(["new", "--full", "blog"], tmp_path, monkeypatch)
    assert rc == 1
