#!/usr/bin/env python3
import subprocess
from pathlib import Path

home = Path.home()
LIVE_PATH = home / ".chrapt" / "live-boxes"
PACKED_PATH = home / ".chrapt" / "packed-boxes"

COLOR_ROOT = "\033[1;35m"
COLOR_BLUE = "\033[0;36m"
COLOR_LOOP = "\033[90m"
COLOR_RESET = "\033[0m"

def tree(package_name, no_unn):
    apt_cache = load_entire_dependency_cache(package_name)
    if no_unn:
        apt_cache = remove_loops(package_name, apt_cache)
    draw_tree(package_name, apt_cache, is_root=True)

def list(package_name, no_unn):
    apt_cache = load_entire_dependency_cache(package_name)
    if not apt_cache:
        print(f"Nothing found under {package_name}")
        return
    packs = set()
    for pkg, deps in apt_cache.items():
        packs.add(pkg)
        for dep in deps:
            packs.add(dep)


    sorted_p = sorted(packs)

    if not no_unn:
        print(f"{COLOR_ROOT}{package_name}{COLOR_RESET} benötigt insgesamt {len(sorted_p)} Pakete:")
        print("-" * 40)
    print(COLOR_BLUE+" ".join(sorted_p)+COLOR_RESET)

def load_entire_dependency_cache(root_package):
    pkg_cache = {}
    try:
        cmd = f"LC_ALL=C apt-cache depends --recurse --no-recommends --no-suggests --no-conflicts --no-breaks --no-replaces --no-enhances {root_package}"
        res = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL)
        current_pkg = None
        for line in res.splitlines():
            if not line.strip():
                continue

            if not line.startswith(" ") and not line.startswith("\t"):
                current_pkg = line.strip()
                pkg_cache[current_pkg] = []
            elif line.strip().startswith("Depends:") and current_pkg:
                dep_name = line.strip().split(":", 1)[1].strip().split()[0]
                if dep_name and not dep_name.startswith("<"):
                    pkg_cache[current_pkg].append(dep_name)

        return pkg_cache
    except:
        return {}

def draw_tree(package, cache, prefix="", is_last=True, seen=None, is_root=False):
    if seen is None:
        seen = set()

    if is_root:
        print(f"{COLOR_ROOT}{package}{COLOR_RESET}")
        seen.add(package)
        deps = cache.get(package, [])

        for i, dep in enumerate(deps):
            draw_tree(dep, cache, prefix="", is_last=(i == len(deps) - 1), seen=seen)
        return

    marker = "╰─ " if is_last else "├─ "
    is_duplicate = package in seen

    if is_duplicate:
        print(f"{prefix}{marker}{COLOR_LOOP}{package} [\u00B7\u00B7\u00B7]{COLOR_RESET}")
        return
    else:
        print(f"{prefix}{marker}{COLOR_BLUE}{package}{COLOR_RESET}")
        seen.add(package)

    deps = cache.get(package, [])

    next_prefix = prefix + ("   " if is_last else "│  ")

    for i, dep in enumerate(deps):
        draw_tree(dep, cache, next_prefix, is_last=(i == len(deps) - 1), seen=seen)

def remove_loops(root_package, apt_cache):
    if not apt_cache:
            return {}
    cleaned_cache = {}
    seen = {root_package}
    def traverse(pkg):
        cleaned_deps = []
        original_deps = apt_cache.get(pkg, [])
        for dep in original_deps:
            if dep not in seen:
                seen.add(dep)
                cleaned_deps.append(dep)
                traverse(dep)
        cleaned_cache[pkg] = cleaned_deps
    traverse(root_package)
    for pkg in apt_cache:
        if pkg not in cleaned_cache:
            cleaned_cache[pkg] = []
    return cleaned_cache

def boxen():
    lp_content = [path.name for path in LIVE_PATH.iterdir() if path.is_dir()]
    pp_content = [path.name for path in PACKED_PATH.glob("*.tar.gz")]
    if lp_content:
        print(COLOR_ROOT + "live" + COLOR_RESET)
    for i, p in enumerate(lp_content):
        if i < len(lp_content)-1:
            print("├─ " + COLOR_BLUE + p + COLOR_RESET)
        else:
            print("╰─ " + COLOR_BLUE + p + COLOR_RESET)
    if pp_content:
        print(COLOR_ROOT + "packed" + COLOR_RESET)
        for i, p in enumerate(pp_content):
            if i < len(pp_content)-1:
                print("├─ " + COLOR_BLUE + p + COLOR_RESET)
            else:
                print("╰─ " + COLOR_BLUE + p + COLOR_RESET)
