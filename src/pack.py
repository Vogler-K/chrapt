#!/usr/bin/env python3
import hashlib
import shutil
import tarfile
from pathlib import Path

home = Path.home()
LIVE_PATH = home / ".chrapt" / "live-boxes"
PACKED_PATH = home / ".chrapt" / "packed-boxes"
SYMLINK_PATH = home / ".chrapt" / "bin"

RUN_SCRIPT = r"""#!/bin/bash
if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Please run a program"
    exit 1
fi

if [ ! -d "$1" ]; then
    echo "Error: The box directory '$1' does not exist! It may be bundled!"
    exit 1
fi

ARGS=("${@:3}")

if [ "${2##*/}" = "bash" ]; then
    ARGS=("--rcfile" "/etc/box_bashrc" "${ARGS[@]}")
fi

USER_ID=$(id -u)
WAYLAND_SOCKET="${XDG_RUNTIME_DIR}/wayland-0"

exec bwrap --bind "$1" / \
--chdir / \
--dev /dev \
--share-net \
--proc /proc \
--ro-bind-try /etc/ssl /etc/ssl \
--dev-bind-try /dev/dri /dev/dri \
--ro-bind-try /etc/fonts /etc/fonts \
--ro-bind-try /lib/terminfo /lib/terminfo \
--ro-bind-try /tmp/.X11-unix /tmp/.X11-unix \
--ro-bind-try /usr/share/X11 /usr/share/X11 \
--ro-bind-try /usr/lib/locale /usr/lib/locale \
--setenv PATH "/usr/bin:/bin:/usr/sbin:/sbin" \
--ro-bind-try /etc/resolv.conf /etc/resolv.conf \
--ro-bind-try /usr/share/fonts /usr/share/fonts \
--ro-bind-try /usr/share/icons /usr/share/icons \
--ro-bind-try /usr/share/themes /usr/share/themes \
--ro-bind-try /usr/share/terminfo /usr/share/terminfo \
--ro-bind-try /usr/share/zoneinfo /usr/share/zoneinfo \
--ro-bind-try /etc/ca-certificates /etc/ca-certificates \
--ro-bind-try /run/user/$USER_ID/bus /run/user/$USER_ID/bus \
--ro-bind-try "$WAYLAND_SOCKET" /run/user/$USER_ID/wayland-0 \
--setenv box $(basename "$1") \
"$2" "${ARGS[@]}"
"""

def bundle(folder):
    live_path = LIVE_PATH / folder
    pack_path = PACKED_PATH / f"{folder}.tar.gz"
    if not live_path.exists():
        print(f"The Box {folder} doesn't exist")
        raise FileNotFoundError
    if pack_path.exists():
        print(f"There is already a compressed {folder}")
        raise FileExistsError
    PACKED_PATH.mkdir(parents=True, exist_ok=True)

    try:
        with tarfile.open(pack_path, mode="w:gz") as tar:
            tar.add(live_path, arcname=folder)
        if live_path.exists() and live_path.is_dir():
            shutil.rmtree(live_path)
    except Exception as e:
        print(f"An error occurred while bundling: {e}")
        if pack_path.exists():
            pack_path.unlink()

def scatter(folder):
    live_path = LIVE_PATH / folder
    pack_path = PACKED_PATH / f"{folder}.tar.gz"
    if not pack_path.exists():
        print(f"The packed Box {folder} doesn't exist")
        raise FileNotFoundError
    if live_path.exists():
        print(f"There is already a uncompressed {folder}")
        raise FileExistsError

    LIVE_PATH.mkdir(parents=True, exist_ok=True)

    try:
        with tarfile.open(pack_path, mode="r:gz") as tar:
            tar.extractall(path=LIVE_PATH)
        if pack_path.exists():
            pack_path.unlink()

    except Exception as e:
        print(f"An error occurred while scattering: {e}")
        if live_path.exists() and live_path.is_dir():
            shutil.rmtree(live_path)
        exit()

    register(folder)

def create_symlink(folder, binary_name, binary_path):
    sh_content = f'#!/bin/bash\nexec "{SYMLINK_PATH.parent / "run"}" "{LIVE_PATH / folder}" "{binary_path+binary_name}" "$@"'
    sh_path = SYMLINK_PATH / f"{folder}-{binary_name}"
    sh_path.write_text(sh_content, encoding="utf-8")
    sh_path.chmod(0o755)

def register(folder):
    usr_bin = LIVE_PATH / folder / "usr" / "bin"
    usr_sbin = LIVE_PATH / folder / "usr" / "sbin"
    run_sh = SYMLINK_PATH.parent / "run"
    if not run_sh.is_file():
        run_sh.parent.mkdir(parents=True, exist_ok=True)
        run_sh.write_text(RUN_SCRIPT, encoding="utf-8")
        run_sh.chmod(0o755)
    else:
        rs_hash = hashlib.sha256(RUN_SCRIPT.encode('utf-8')).hexdigest()
        file_hasher = hashlib.sha256()
        with open(run_sh, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                file_hasher.update(chunk)
        if rs_hash != file_hasher.hexdigest():
            run_sh.write_text(RUN_SCRIPT, encoding="utf-8")
            run_sh.chmod(0o755)
    SYMLINK_PATH.mkdir(parents=True, exist_ok=True)
    for binary_path in usr_bin.iterdir():
        if binary_path.is_file():
            create_symlink(folder, binary_path.name, "/usr/bin/")
    for binary_path in usr_sbin.iterdir():
        if binary_path.is_file():
            create_symlink(folder, binary_path.name, "/usr/sbin/")
