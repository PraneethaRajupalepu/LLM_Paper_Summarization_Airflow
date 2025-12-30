import os
import shlex
from typing import Optional


def _manual_load(env_path: str, overwrite: bool) -> bool:
    """Fallback simple parser for KEY=VALUE lines if python-dotenv isn't present."""
    if not os.path.exists(env_path):
        return False

    with open(env_path, "r", encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip()
            if (val.startswith('"') and val.endswith('"')) or (
                val.startswith("'") and val.endswith("'")
            ):
                val = val[1:-1]
            # Try to unescape common shell escapes
            try:
                parts = shlex.split(val)
                if parts:
                    val = parts[0]
            except Exception:
                pass
            if overwrite or key not in os.environ:
                os.environ[key] = val
    return True


def load_env(env_path: str = "e.env", overwrite: bool = False) -> bool:
    """Load environment variables from `env_path`.

    Behavior:
    - If `python-dotenv` is installed, use its `load_dotenv` loader (preferred).
      This preserves correct parsing for common .env formats.
    - Otherwise fall back to a lightweight builtin parser.
    - `overwrite=True` will replace existing env vars when possible.

    Returns True if a file was found and parsed (or dotenv reported success),
    False if the file wasn't present.
    """
    # Prefer python-dotenv if available
    try:
        from dotenv import load_dotenv as _load_dotenv  # type: ignore
    except Exception:
        _load_dotenv = None

    if _load_dotenv:
        # python-dotenv's load_dotenv returns True/False depending on whether
        # the file was successfully parsed. Newer versions accept `override`.
        try:
            # Try to use override parameter if available
            return bool(_load_dotenv(env_path, override=overwrite))
        except TypeError:
            # Older versions might not support override; call without it and
            # enforce overwrite by manually re-reading if requested.
            ok = bool(_load_dotenv(env_path))
            if ok and overwrite:
                # Re-apply by reading the file and setting env vars directly
                return _manual_load(env_path, overwrite=True)
            return ok

    # Fallback to manual loader
    return _manual_load(env_path, overwrite)


if __name__ == "__main__":
    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else "e.env"
    ok = load_env(path, overwrite=False)
    print(f"Loaded: {ok} -> {path}")
