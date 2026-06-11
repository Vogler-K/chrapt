#!/usr/bin/env python3
import argparse
from pathlib import Path

import install
import pack
import tree

home = Path.home()
SYMLINK_PATH = home / ".chrapt" / "bin"

def main():
    parser = argparse.ArgumentParser(
        description="chrapt - A modular, isolated package manager for executing software packages in autarkic sandboxes (boxes) using bubblewrap ≽(•⩊•マ≼"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=False,
        help=""
    )

    tree_subc(subparsers)
    install_subc(subparsers)
    pack_subc(subparsers)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
    elif args.command == "tree":
        if not args.list:
            tree.tree(args.packet, args.no_unn)
        else:
            tree.list(args.packet, args.no_unn)
    elif args.command == "install":
        install.install(args.folder, args.packets, advanced_mode=args.advanced)
    elif args.command == "remove":
        install.remove(args.folder)
    elif args.command == "list":
        tree.boxen()
    elif args.command == "bundle":
        pack.bundle(args.folder)
    elif args.command == "scatter":
        pack.scatter(args.folder)

def tree_subc(subparsers):
    tree_parser = subparsers.add_parser(
        "tree",
        help="Analyzes and visualizes the dependency tree of a Debian package"
    )
    tree_parser.add_argument(
        "packet",
        type=str,
        help="Name of the source or binary package to analyze"
    )
    tree_parser.add_argument(
        "--no-unn",
        "-n",
        action="store_true",
        help="Filters out unnecessary or redundant package dependencies from the analysis"
    )
    tree_parser.add_argument(
        "--list",
        "-l",
        action="store_true",
        help="Outputs the determined package dependencies as a flat, sorted text list instead of a tree structure"
    )

    list_parser = subparsers.add_parser(
        "list",
        help="Lists all existing boxes (split into active 'live' folders and archived 'packed' files)"
    )

def install_subc(subparsers):
    install_parser = subparsers.add_parser(
        "install",
        help="Creates a new box or installs packages and their dependencies into an existing box"
    )
    install_parser.add_argument(
        "folder",
        type=str,
        help="Name of the target directory (the box) underneath ~/.chrapt/live-boxes/"
    )
    install_parser.add_argument(
        "packets",
        type=str,
        nargs="+",
        help="List of Debian packages to install (separated by spaces)"
    )
    install_parser.add_argument(
        "--advanced",
        action="store_true",
        help="Allows the installation of critical system packages (e.g., systemd, sysv) that are blocked by default, because the WON'T work properly"
    )

    del_parser = subparsers.add_parser(
        "remove",
        help="Permanently deletes a box from the system (removes live folders, archives, and all binary symlinks from the PATH"
    )
    del_parser.add_argument(
        "folder",
        help="Name of the box to delete",
        type=str
    )

def pack_subc(subparsers):
    bundle_parser = subparsers.add_parser(
        "bundle",
        help="Freezes an active live box (compresses it into a .tar.gz file and deletes the live directory)"
    )
    bundle_parser.add_argument(
        "folder",
        type=str,
        help="Name of the box to freeze"
    )

    scatter_parser = subparsers.add_parser(
        "scatter",
        help="Thaws an archived box (extracts the .tar.gz file into the live folder and re-registers the symlinks)"
    )
    scatter_parser.add_argument(
        "folder",
        type=str,
        help="Name of the box to restore"
    )

def ensure_path_env():
    bin_dir_str = str(SYMLINK_PATH).replace(str(Path.home()), "$HOME")
    export_line = f'export PATH="{bin_dir_str}:$PATH"\n'
    shell_rc = Path.home() / ".bashrc"
    if shell_rc.exists():
         content = shell_rc.read_text(encoding="utf-8")
         if bin_dir_str in content:
             return

    with open(shell_rc, "a", encoding="utf-8") as f:
         f.write("\n# This has been and will be added automatically by chrapt\n")
         f.write(export_line)

if __name__ == "__main__":
    # ensure_path_env()
    main()
