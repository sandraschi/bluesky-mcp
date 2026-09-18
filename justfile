set windows-shell := ["powershell.exe", "-NoProfile", "-Command"]

default:
    @just --list

UV := "C:\\Users\\sandr\\.local\\bin\\uv.exe"
REPO := "D:\\Dev\\repos\\bluesky-mcp"

install:
    & "{{UV}}" sync

serve:
    Set-Location "{{REPO}}"; powershell.exe -NoProfile -ExecutionPolicy Bypass -File start.ps1

dev: serve

lint:
    & "{{UV}}" run ruff check src tests
    & "{{UV}}" run ruff format --check src tests

fmt:
    & "{{UV}}" run ruff check --fix src tests
    & "{{UV}}" run ruff format src tests

test:
    & "{{UV}}" run python -m pytest -q tests/

ci:
    & "{{UV}}" run ruff check src tests
    & "{{UV}}" run ruff format --check src tests
    & "{{UV}}" run pyright src
    & "{{UV}}" run python -m pytest -q tests/
    Set-Location "{{REPO}}\\webapp"; npm run check; npm run biome:ci

certify: lint test
    & "{{UV}}" run pyright src
    Set-Location "{{REPO}}\\webapp"; npm run check; npm run biome:ci

bootstrap:
    & "{{UV}}" sync
    pre-commit install
    Set-Location "{{REPO}}\\webapp"; npm ci

test-e2e:
    Set-Location "{{REPO}}\\webapp"; npm run test:e2e

# Pre-Tauri browser walk (dev-loop CUA test)
cua-webapp-test:
    Set-Location "{{REPO}}"; powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/just/cua-webapp-test.ps1

# NSIS smoke test (install -> launch -> nav walk -> uninstall)
cua-nsis-test:
    Set-Location "{{REPO}}"; powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/just/cua-nsis-test.ps1

# Bundle MCP server for Claude Desktop (MCPB)
mcpb-pack:
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "D:\Dev\repos\mcp-central-docs\scripts\make-mcpb.ps1" -RepoPath "{{REPO}}"

# Tauri NSIS release build (requires icons, PyInstaller spec, webapp dist)
build-native:
    $env:Path = "$env:USERPROFILE\\.cargo\\bin;$env:Path"
    Set-Location "{{REPO}}"; powershell.exe -NoProfile -ExecutionPolicy Bypass -File src-tauri/build.ps1

# Tauri debug build (skip PyInstaller when backend exe already in resources/)
build-native-debug:
    $env:Path = "$env:USERPROFILE\\.cargo\\bin;$env:Path"; Set-Location "{{REPO}}\\src-tauri"; npx @tauri-apps/cli build --debug
