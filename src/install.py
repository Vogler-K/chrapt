#!/usr/bin/env python3
import os
import shutil
import subprocess
from pathlib import Path

import pack

home = Path.home()
LIVE_PATH = home / ".chrapt" / "live-boxes"
PACKED_PATH = home / ".chrapt" / "packed-boxes"
SYMLINK_PATH = home / ".chrapt" / "bin"
DEB_PATH = home / ".chrapt" / "cache"

def install(folder, packets, advanced_mode=False):
    if not folder.isalnum():
        print(f"The foldername '{folder}' may only use alphanumeric characters")
        return
    if len(folder) > 255:
        print(f"The foldername '{folder}' is not valid")
        return

    clean_up_first(folder)
    downloads = download(folder, packets, advanced_mode)[0]
    if not downloads:
        exit()
    patch(folder, downloads)
    clean_up_after(folder)

def remove(folder):
    dir_path = LIVE_PATH / folder
    deb_path = DEB_PATH / folder
    file_path = PACKED_PATH / f"{folder}.tar.gz"
    if dir_path.exists() and dir_path.is_dir():
        shutil.rmtree(dir_path)
    if deb_path.exists() and deb_path.is_dir():
        shutil.rmtree(deb_path)
    if file_path.exists() and file_path.is_file():
        file_path.unlink()
    if SYMLINK_PATH.exists():
        for item in SYMLINK_PATH.glob(f"{folder}-*"):
            if item.is_file():
                item.unlink()


def clean_up_first(folder):
    deb_path = DEB_PATH / folder
    pack_path = LIVE_PATH / folder
    bundled_file = PACKED_PATH / f"{folder}.tar.gz"
    deb_path.mkdir(parents=True, exist_ok=True)
    PACKED_PATH.mkdir(parents=True, exist_ok=True)
    if bundled_file.exists():
        pack.scatter(folder)
    else:
        if not (LIVE_PATH / folder).exists():
            pack_path.mkdir(parents=True, exist_ok=True)
            core_packets = ["bash", "busybox-static"]
            core_downloads, err = download(folder, core_packets, advanced_mode=False, critical=True)
            if not core_downloads or err:
                print(f"There was an error installing bash or busybox-static, box will be deleted")
                remove(folder)
                exit()
            patch(folder, core_downloads)
            os.makedirs(pack_path / "etc", exist_ok=True)
            username = os.getlogin()
            for file in ["passwd", "group"]:
                try:
                    with open(f"/etc/{file}", "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    user_lines = [l for l in lines if l.startswith(f"{username}:")]
                    box_file_path = pack_path / "etc" / file
                    with open(box_file_path, "w", encoding="utf-8") as f_out:
                        f_out.writelines(user_lines)

                except FileNotFoundError:
                    print(f"Warning: /etc/{file} not found on host system.")

            with open(pack_path/"etc"/"box_bashrc", "w", encoding="utf-8") as f:
                f.writelines(r"""source /etc/bash.bashrc 2>/dev/null
source ~/.bashrc 2>/dev/null

export BLUE_BOLD='\[\033[01;34m\]'
export RED_BOLD='\[\033[01;31m\]'
export RESET='\[\033[00m\]'

export PS1="${BLUE_BOLD}($box) ${RESET}${RED_BOLD}\u@\h${RESET}:${RESET}\w\\$ """)
        else:
            pack_path.mkdir(parents=True, exist_ok=True)


    os.makedirs(os.path.join(pack_path, "usr/bin"), exist_ok=True)
    os.makedirs(os.path.join(pack_path, "usr/sbin"), exist_ok=True)
    os.makedirs(os.path.join(pack_path, "usr/lib"), exist_ok=True)
    os.makedirs(os.path.join(pack_path, "usr/lib64"), exist_ok=True)




    links = {
        "bin": "usr/bin",
        "sbin": "usr/sbin",
        "lib": "usr/lib",
        "lib64": "usr/lib64"
    }
    for link, real_folder in links.items():
        full_link_path = os.path.join(pack_path, link)
        if not os.path.exists(full_link_path) and not os.path.islink(full_link_path):
            os.symlink(real_folder, full_link_path)

def download(folder, packets, advanced_mode, critical=False):
    packets = [p for p in packets if p.strip()]
    deb_path = DEB_PATH / folder
    files_before = set(deb_path.glob("*.deb"))
    all_deps = set()
    advanced_pack_found = False
    advaced_packs = set((
            "systemd",
            "sysv",
            "grub-",
            "init-system",
            "linux-image",
            "initramfs",
            "kmod"
        ))
    for packet in packets:
        cmd = fr"apt-cache depends --recurse --no-recommends --no-suggests --no-conflicts --no-breaks --no-replaces --no-enhances {packet} | grep '^\w'"
        try:
            res = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL)
            current_deps = set(p.strip() for p in res.split("\n") if p.strip())
            illegal = [
                dep for dep in current_deps
                if any(bad_pkg in dep for bad_pkg in advaced_packs)
            ]
            if illegal:
                print(f"The package {packet} requires an advanced packet ({', '.join(illegal)})")
                advanced_pack_found = True
            all_deps.update(current_deps)
        except:
            print(f"The package {packet} wasn't found, make sure you have your apt lists updated, it will NOT be installed now")
            if critical:
                return None, "._."
    if advanced_pack_found:
        if not advanced_mode:
            exit()
        else:
            print("\033[1;31mYou are using advanced mode and use packages which won't work in 99% of cases! Good Luck!\033[0m")
    if not all_deps:
        return None, "._."
    download_list = " ".join(sorted(all_deps))
    cmd = fr"LC_ALL=C apt-get download {download_list}"
    subprocess.run(cmd, shell=True, cwd=deb_path, check=True)
    files_after = set(deb_path.glob("*.deb"))
    return list(files_after-files_before), None

def patch(folder, downloads):
    if not downloads:
        return
    pack_path = LIVE_PATH / folder
    manifest = pack_path / ".chrapt-list"
    installed_packets = set()
    patched_packets = set()

    for file in downloads:
        cmd = fr"dpkg -x {file} {pack_path}"
        subprocess.run(cmd, shell=True, stderr=subprocess.DEVNULL)
        patched_packets.add(file.stem)

    if manifest.exists():
        with open(manifest, "r", encoding='utf-8') as f:
            installed_packets = set(line.strip() for line in f if line.strip())

    def set_to_dict(s):
        return {item.split("_")[0]: item for item in s}

    installed_dict = set_to_dict(installed_packets)
    patched_dict = set_to_dict(patched_packets)
    merged_dict = installed_dict | patched_dict
    merged_set = set(merged_dict.values())

    with open(manifest, "w") as f:
        for packet in sorted(merged_set):
                f.write(f"{packet}\n")

def clean_up_after(folder):
    pack_path = LIVE_PATH / folder
    deb_path = DEB_PATH / folder
    os.makedirs(pack_path / "etc", exist_ok=True)
    if deb_path.exists() and deb_path.is_dir():
        shutil.rmtree(deb_path)
    pack.register(folder)
