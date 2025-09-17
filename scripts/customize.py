#!/usr/bin/env python3
"""
Interactive repository customizer for Home Assistant integration blueprint.

This script:
- Parses the Git origin to infer `username/repo`.
- Prompts for confirmation and integration naming (snake_case and CamelCaps).
- Renames the `custom_components/integration_blueprint` package to the chosen name.
- Updates references across the repo (excluding README.md).
- Adjusts manifest domain/name and optionally updates devcontainer settings.
"""

# ruff: noqa: T201

import configparser
import contextlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


def read_origin_from_git_config(repo_root: Path) -> str | None:
    """
    Return the remote.origin URL using best-effort strategies:
    1) Read from the Git config file, handling both .git directory and .git file (worktrees/submodules).
    2) Fallback to `git config --get remote.origin.url`.
    """
    def _parse_config(config_path: Path) -> str | None:
        parser = configparser.ConfigParser()
        try:
            parser.read(config_path)
        except (OSError, configparser.Error):
            return None
        for section in parser.sections():
            if section.strip() == 'remote "origin"' and parser.has_option(section, "url"):
                return parser.get(section, "url").strip()
        return None

    # Case 1: standard .git directory
    git_path = repo_root / ".git"
    if git_path.is_dir():
        git_config_path = git_path / "config"
        if git_config_path.exists():
            url = _parse_config(git_config_path)
            if url:
                return url

    # Case 2: .git is a file pointing to actual gitdir (e.g., worktree)
    if git_path.is_file():
        try:
            content = git_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            content = ""
        m = re.search(r"gitdir:\s*(.+)\s*", content)
        if m:
            gitdir_raw = m.group(1).strip()
            gitdir_path = Path(gitdir_raw)
            # If relative path, resolve relative to repo root
            if not gitdir_path.is_absolute():
                gitdir_path = (repo_root / gitdir_path).resolve()
            git_config_path = gitdir_path / "config"
            if git_config_path.exists():
                url = _parse_config(git_config_path)
                if url:
                    return url

    # Case 3: fallback to calling git
    try:
        proc = subprocess.run(  # noqa: S603
            ("git", "config", "--get", "remote.origin.url"),
            cwd=str(repo_root),
            check=False,
            capture_output=True,
            text=True,
        )
        url = (proc.stdout or "").strip()
        if url:
            return url
    except (FileNotFoundError, OSError):
        pass

    return None


def parse_username_repo_from_origin(origin_url: str) -> tuple[str | None, str | None]:
    """Extract `username` and `repo` from a GitHub origin URL."""
    if not origin_url:
        return None, None
    # Support git@github.com:username/repo(.git) and https://github.com/username/repo(.git)
    m = re.search(r"github\.com[/:]([^/]+)/([^/]+?)(?:\.git)?$", origin_url)
    if not m:
        return None, None
    username = m.group(1)
    repo = m.group(2)
    return username, repo


def guess_integration_name_from_repo(repo_name: str) -> str:
    """Guess a human-friendly base name from the repository name."""
    base = repo_name or "integration_blueprint"
    # Remove common prefixes/suffixes
    base = re.sub(
        r"^(home[-_]?assistant[-_]?|ha[-_]?|hass[-_]?|integration[-_]?|custom[-_]?component[-_]?)+",
        "",
        base,
        flags=re.IGNORECASE,
    )
    base = re.sub(r"[-_]?integration$", "", base, flags=re.IGNORECASE)
    return base.strip("-_ ") or repo_name


def to_snake_case(name: str) -> str:
    """Convert a name to snake_case."""
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", name)
    cleaned = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", cleaned)
    cleaned = cleaned.strip("_")
    return re.sub(r"_+", "_", cleaned).lower()


def to_camel_caps(name: str) -> str:
    """Convert a name to CamelCaps, preserving existing CamelCase/PascalCase.

    - If the input is already camel/PascalCase without separators, keep it (ensure leading capital).
    - Otherwise, split on non-alphanumerics and title-case each token.
    """
    # Already camel-like and contains both lower and upper letters
    if re.match(r"^[A-Za-z0-9]+$", name) and re.search(r"[a-z][A-Z]", name):
        return name[:1].upper() + name[1:]

    parts = re.split(r"[^A-Za-z0-9]+", name)
    parts = [p for p in parts if p]
    return "".join(p[:1].upper() + p[1:].lower() for p in parts)


def prompt_with_default(prompt: str, default: str | None) -> str:
    """Prompt for input, returning default if no response is provided."""
    full = f"{prompt} [{default}]: " if default else f"{prompt}: "
    resp = input(full).strip()
    return resp or (default or "")


def confirm_yes_no(prompt: str, *, default_yes: bool = True) -> bool:
    """Ask a yes/no question; return True/False. Boolean is keyword-only."""
    suffix = "[Y/n]" if default_yes else "[y/N]"
    while True:
        resp = input(f"{prompt} {suffix} ").strip().lower()
        if not resp:
            return default_yes
        if resp in {"y", "yes"}:
            return True
        if resp in {"n", "no"}:
            return False


def replace_text_in_file(path: Path, replacements: tuple[tuple[str, str], ...]) -> bool:
    """Replace simple string pairs in a text file; return True if changed."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    original = text
    for old, new in replacements:
        text = text.replace(old, new)
    if text != original:
        try:
            path.write_text(text, encoding="utf-8")
        except OSError:
            return False
        return True
    return False


def update_manifest(manifest_path: Path, domain: str, display_name: str) -> None:
    """Update manifest `domain` and `name` if needed."""
    if not manifest_path.exists():
        return
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return
    changed = False
    if data.get("domain") != domain:
        data["domain"] = domain
        changed = True
    # Update name to display_name if clearly blueprint-ish or missing
    if not data.get("name") or "blueprint" in str(data.get("name", "")).lower():
        data["name"] = display_name
        changed = True
    if changed:
        try:
            manifest_path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
        except OSError:
            return


def ensure_cursor_editor_in_devcontainer(repo_root: Path) -> None:
    """Set GIT_EDITOR to `cursor` in devcontainer if present."""
    devcontainer = repo_root / ".devcontainer.json"
    if not devcontainer.exists():
        return
    try:
        cfg = json.loads(devcontainer.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return
    remote_env = cfg.get("remoteEnv", {})
    if remote_env.get("GIT_EDITOR") != "cursor":
        remote_env["GIT_EDITOR"] = "cursor"
        cfg["remoteEnv"] = remote_env
        try:
            devcontainer.write_text(
                json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
        except OSError:
            return


def update_vscode_extensions_in_devcontainer(
    repo_root: Path, desired: dict[str, bool]
) -> None:
    """Add/remove VSCode extensions in devcontainer according to `desired` flags."""
    devcontainer = repo_root / ".devcontainer.json"
    if not devcontainer.exists():
        return
    try:
        cfg = json.loads(devcontainer.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return
    customizations = cfg.setdefault("customizations", {})
    vscode = customizations.setdefault("vscode", {})
    extensions = vscode.setdefault("extensions", [])

    changed = False
    # Normalize to set for faster membership checks
    current = list(extensions)
    current_set = set(current)

    for ext_id, should_have in desired.items():
        if should_have and ext_id not in current_set:
            current.append(ext_id)
            current_set.add(ext_id)
            changed = True
        if not should_have and ext_id in current_set:
            current = [e for e in current if e != ext_id]
            current_set.discard(ext_id)
            changed = True

    if changed:
        vscode["extensions"] = current
        try:
            devcontainer.write_text(
                json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
        except OSError:
            return


def ensure_line_in_file(path: Path, line: str) -> bool:
    """Append `line` to file if not already present; returns True if changed."""
    try:
        text = path.read_text(encoding="utf-8") if path.exists() else ""
    except (OSError, UnicodeDecodeError):
        return False
    if line in text:
        return False
    # Ensure file ends with newline before appending
    new_text = text
    if new_text and not new_text.endswith("\n"):
        new_text += "\n"
    new_text += line + "\n"
    try:
        path.write_text(new_text, encoding="utf-8")
    except OSError:
        return False
    return True


def ensure_precommit_requirement(req_path: Path, version_pin: str = "3.5.0") -> bool:
    """Ensure `pre_commit==<version_pin>` exists in requirements; update if needed."""
    try:
        lines = (
            req_path.read_text(encoding="utf-8").splitlines()
            if req_path.exists()
            else []
        )
    except (OSError, UnicodeDecodeError):
        return False
    pin_line = f"pre_commit=={version_pin}"
    changed = False
    found_index: int | None = None
    for idx, raw in enumerate(lines):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        # Match pre-commit in either hyphen/underscore form
        if re.match(r"^pre[-_]?commit\s*==\s*[^\s#]+$", line, flags=re.IGNORECASE):
            found_index = idx
            if line != pin_line:
                lines[idx] = pin_line
                changed = True
            break
    if found_index is None:
        lines.append(pin_line)
        changed = True
    if changed:
        try:
            req_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        except OSError:
            return False
    return changed


def ensure_dod_in_devcontainer(repo_root: Path) -> bool:
    """
    Ensure Docker-outside-of-Docker feature and docker.sock mount are set.

    Returns True if the file was modified.
    """
    devcontainer = repo_root / ".devcontainer.json"
    if not devcontainer.exists():
        return False
    try:
        cfg = json.loads(devcontainer.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return False

    changed = False

    # Ensure features
    features = cfg.setdefault("features", {})
    dod_key = "ghcr.io/devcontainers/features/docker-outside-of-docker:1"
    dod_cfg = features.get(dod_key)
    if not isinstance(dod_cfg, dict) or dod_cfg.get("moby") is None:
        features[dod_key] = {"moby": False}
        changed = True

    # Ensure mounts array includes docker.sock bind
    mounts = cfg.setdefault("mounts", [])
    bind_line = "source=/var/run/docker.sock,target=/var/run/docker.sock,type=bind"
    if bind_line not in mounts:
        mounts.append(bind_line)
        changed = True

    if changed:
        try:
            devcontainer.write_text(
                json.dumps(cfg, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        except OSError:
            return False
    return changed


def is_git_repo(repo_root: Path) -> bool:
    """Return True if the directory appears to be a Git repository."""
    return (repo_root / ".git").exists()


def rename_with_git_mv(old_path: Path, new_path: Path, repo_root: Path) -> bool:
    """
    Rename using `git mv` to preserve history; fall back to filesystem move.

    Returns True if a rename was performed.
    """
    if not old_path.exists():
        return False
    if new_path.exists():
        return False
    new_path.parent.mkdir(parents=True, exist_ok=True)
    if is_git_repo(repo_root):
        try:
            # Use `-k` to skip errors for unrelated collisions; we guard above anyway
            subprocess.run(  # noqa: S603 - fixed argv; no shell; trusted executable
                (
                    "git",
                    "mv",
                    "-k",
                    "--",
                    str(old_path),
                    str(new_path),
                ),
                cwd=str(repo_root),
                check=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            shutil.move(str(old_path), str(new_path))
        else:
            return True
    else:
        shutil.move(str(old_path), str(new_path))
    return True


def main() -> int:  # noqa: PLR0912, PLR0915
    """Run interactive customization."""
    repo_root = Path(__file__).resolve().parents[1]

    origin_url = read_origin_from_git_config(repo_root)
    guessed_user, guessed_repo = parse_username_repo_from_origin(origin_url or "")

    print("Detected origin:", origin_url or "<none>")
    username = prompt_with_default("GitHub username", guessed_user or "")
    repo_name = prompt_with_default("Repository name", guessed_repo or repo_root.name)

    if not confirm_yes_no(
        f"Confirm repository as {username}/{repo_name}?", default_yes=True
    ):
        print("Aborted by user.")
        return 1

    guessed_integration_base = guess_integration_name_from_repo(repo_name)
    integration_input = prompt_with_default(
        "Integration name", guessed_integration_base
    )
    snake = to_snake_case(integration_input)
    camel = to_camel_caps(integration_input)

    print(f"Using integration identifiers -> snake_case: {snake}, CamelCaps: {camel}")
    if not confirm_yes_no("Proceed with these names?", default_yes=True):
        print("Aborted by user.")
        return 1

    # Prepare replacements (exclude README.md)
    replacements: tuple[tuple[str, str], ...] = (
        ("ludeeus/integration_blueprint", f"{username}/{repo_name}"),
        ("custom_components/integration_blueprint", f"custom_components/{snake}"),
    )

    excluded_files = {
        str(repo_root / "README.md"),
        str(repo_root / "scripts" / "customize.py"),
    }
    excluded_dirs = {
        ".git",
        "__pycache__",
        ".venv",
        "node_modules",
        ".pytest_cache",
        ".mypy_cache",
    }

    changed_files = 0
    for path in repo_root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in excluded_dirs for part in path.parts):
            continue
        if str(path) in excluded_files:
            continue
        # Skip binary-ish files by extension
        if path.suffix.lower() in {
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".ico",
            ".woff",
            ".woff2",
            ".ttf",
            ".otf",
            ".zip",
            ".gz",
        }:
            continue
        # Blueprint → CamelCaps integration name inside component code
        extra_replacements: tuple[tuple[str, str], ...] = (
            ("IntegrationBlueprint", camel),
            ("Blueprint", camel),
        )
        if replace_text_in_file(path, replacements) or replace_text_in_file(
            path, extra_replacements
        ):
            changed_files += 1

    # Rename custom component directory
    old_pkg_dir = repo_root / "custom_components" / "integration_blueprint"
    new_pkg_dir = repo_root / "custom_components" / snake
    if old_pkg_dir.exists() and old_pkg_dir.is_dir():
        if new_pkg_dir.exists():
            print(f"Target directory already exists: {new_pkg_dir}")
        elif rename_with_git_mv(old_pkg_dir, new_pkg_dir, repo_root):
            print("Renamed component directory using git to preserve history.")

    # Update manifest.json (domain and name)
    manifest_path_candidates = [
        repo_root / "custom_components" / snake / "manifest.json",
        repo_root / "custom_components" / "integration_blueprint" / "manifest.json",
    ]
    for manifest_path in manifest_path_candidates:
        if manifest_path.exists():
            update_manifest(manifest_path, domain=snake, display_name=camel)
            break

    # Editor preference
    editor_choice = prompt_with_default("Editor (Cursor/VSCode)", "Cursor")
    if editor_choice.strip().lower().startswith("cursor"):
        ensure_cursor_editor_in_devcontainer(repo_root)
        print('Configured ".devcontainer.json" with remoteEnv.GIT_EDITOR = "cursor"')
    else:
        print("Skipping Cursor-specific devcontainer configuration.")

    # VSCode extensions choice
    devcontainer = repo_root / ".devcontainer.json"
    # Read existing extensions (unused for defaults since defaults are Yes now)
    if devcontainer.exists():
        with contextlib.suppress(OSError, UnicodeDecodeError, json.JSONDecodeError):
            _ = json.loads(devcontainer.read_text(encoding="utf-8"))

    want_chatgpt = confirm_yes_no(
        'Include VSCode extension "OpenAI ChatGPT" (openai.chatgpt)?',
        default_yes=True,
    )
    want_gha = confirm_yes_no(
        'Include VSCode extension "GitHub Actions" (github.vscode-github-actions)?',
        default_yes=True,
    )
    want_ghla = confirm_yes_no(
        "Include VSCode extension 'GitHub Local Actions' "
        "(SanjulaGanepola.github-local-actions)?",
        default_yes=True,
    )

    update_vscode_extensions_in_devcontainer(
        repo_root,
        {
            "openai.chatgpt": want_chatgpt,
            "github.vscode-github-actions": want_gha,
            "SanjulaGanepola.github-local-actions": want_ghla,
        },
    )

    # If GitHub Local Actions requested, ensure `act` is installed in setup script
    if want_ghla:
        setup_path = repo_root / "scripts" / "setup"
        act_install = (
            "curl --proto '=https' --tlsv1.2 -sSf "
            "https://raw.githubusercontent.com/nektos/act/master/install.sh | "
            "sudo BINDIR=/usr/local/bin bash"
        )
        ensure_line_in_file(setup_path, act_install)

    # Pre-commit option
    if confirm_yes_no("Enable pre-commit hooks?", default_yes=True):
        # Add requirement pin
        ensure_precommit_requirement(
            repo_root / "requirements.txt", version_pin="3.5.0"
        )
        # Ensure install step in setup script
        setup_path = repo_root / "scripts" / "setup"
        ensure_line_in_file(setup_path, "pre-commit install")

    # Docker outside-of-Docker support (useful for GitHub Local Actions)
    want_dod = confirm_yes_no(
        "Enable Docker outside-of-Docker (feature + docker.sock mount)?",
        default_yes=True,
    )
    if want_dod:
        ensure_dod_in_devcontainer(repo_root)

    print("Done. Files changed:", changed_files)
    print("If you are using git, review changes with: git status && git diff")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit(1)
