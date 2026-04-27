#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

current_branch="$(git branch --show-current)"

if [[ -n "$(git status --porcelain)" ]]; then
    echo "Hay cambios sin commit o sin guardar. Hace commit o stash antes de sincronizar."
    exit 1
fi

if [[ "$current_branch" != "main" ]]; then
    echo "Cambiando de $current_branch a main"
    git switch main
fi

echo "Trayendo cambios desde upstream/main"
git fetch upstream main

echo "Integrando cambios en main"
git merge --no-ff upstream/main

echo "Subiendo main actualizado a origin"
git push origin main

echo "Sincronizacion completa: main quedo alineada con upstream y publicada en origin."