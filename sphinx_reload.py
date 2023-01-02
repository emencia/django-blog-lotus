#!/usr/bin/env python
"""
A script to launch a livereload server to watch and rebuild documentation
on some sources changes.

You need to have installed package with extra requirements ``dev`` to use it.

Once launched, server will be available on port 8002, like: ::

    http://localhost:8002/

Borrowed from: ::

    https://livereload.readthedocs.io/en/latest/#script-example-sphinx

"""
from livereload import Server, shell


server = Server()

# Watch root documents (not recursive)
server.watch(
    'docs/*.rst',
    shell(
        'make html',
        cwd='docs'
    )
)

# Watch application core documents
server.watch(
    'docs/core/*.rst',
    shell(
        'make html',
        cwd='docs'
    )
)

# Watch Python modules for autodoc review
server.watch(
    'lotus/*.py',
    shell(
        'make html',
        cwd='docs'
    )
)
server.watch(
    'lotus/*/**.py',
    shell(
        'make html',
        cwd='docs'
    )
)

# Serve the builded documentation
server.serve(
    root='docs/_build/html',
    port=8002,
    host="0.0.0.0",
)
