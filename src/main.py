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
        description=""
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
        help=""
    )
    tree_parser.add_argument(
        "packet",
        type=str,
        help=""
    )
    tree_parser.add_argument(
        "--no-unn",
        "-n",
        action="store_true",
        help=""
    )
    tree_parser.add_argument(
        "--list",
        "-l",
        action="store_true",
        help=""
    )

    list_parser = subparsers.add_parser(
        "list",
        help=""
    )

def install_subc(subparsers):
    install_parser = subparsers.add_parser(
        "install",
        help=""
    )
    install_parser.add_argument(
        "folder",
        type=str,
        help=""
    )
    install_parser.add_argument(
        "packets",
        type=str,
        nargs="+",
        help=""
    )
    install_parser.add_argument(
        "--advanced",
        action="store_true",
        help=""
    )

    del_parser = subparsers.add_parser(
        "remove",
        help=""
    )
    del_parser.add_argument(
        "folder",
        type=str
    )

def pack_subc(subparsers):
    bundle_parser = subparsers.add_parser(
        "bundle",
        help=""
    )
    bundle_parser.add_argument(
        "folder",
        type=str,
        help=""
    )

    scatter_parser = subparsers.add_parser(
        "scatter",
        help=""
    )
    scatter_parser.add_argument(
        "folder",
        type=str,
        help=""
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
