#!/bin/bash

REPO_URL="https://github.com/anupmoncy/execdiff"
ICON_PATH="/Users/anup-admin/Downloads/mivobox_128x128.png"

npm install -g vsce

rm -rf execdiff-vscode
mkdir execdiff-vscode
cd execdiff-vscode

npm init -y > /dev/null

cat > LICENSE <<LIC
MIT License
Copyright (c) 2026 Mivobox
Permission is hereby granted...
LIC

cat > README.md <<MD
# ExecDiff – Trace AI Copilot Runtime Changes

Trace filesystem and dependency changes made by AI copilots during execution.

Install:

pip install execdiff

Run:

execdiff trace
MD

cat > package.json <<JSON
{
  "name": "execdiff",
  "displayName": "ExecDiff – Trace AI Copilot Runtime Changes",
  "description": "Trace filesystem and dependency changes made by AI copilots during execution.",
  "version": "0.0.8",
  "publisher": "mivobox",
  "engines": {
    "vscode": "^1.70.0"
  },
  "extensionKind": [
    "ui"
  ],
  "categories": [
    "Other"
  ],
  "activationEvents": [
    "onCommand:execdiff.info"
  ],
  "contributes": {
    "commands": [
      {
        "command": "execdiff.info",
        "title": "ExecDiff Info"
      }
    ]
  },
  "main": "./extension.js",
  "repository": {
    "type": "git",
    "url": "$REPO_URL"
  },
  "homepage": "https://mivobox.com",
  "icon": "icon.png"
}
JSON

cat > extension.js <<JS
function activate(context) {}
function deactivate() {}
module.exports = { activate, deactivate };
JS

cp $ICON_PATH icon.png

vsce package
