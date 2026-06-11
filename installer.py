#!/usr/bin/env python3
import os
import shutil
import subprocess
from pathlib import Path


def chrapt_installer():
    print("This is chrapt (chroot apt) installer ≽(•⩊•マ≼")
    if os.getuid() == 0:
        print("> Do not run this script as root")
        exit(1)

    print("What does this scipt do?")
    print(" + 1st This script uses apt to update your package lists and install bubblewrap")
    print(" + 2nd This script uses a temporary venv to bundle the src folder to a file in ~/.local/bin/")
    print(" + 3rd This script creates the folder ~/.chrapt/")
    print(" + 4th This script adds a line to your .bashrc to add ~/.chrapt/bin/ to your PATH")
    if input("Do you want that? (type 'YES ok'): ").strip() != 'YES ok':
        print("> Aborting")
        exit(1)
    print("> Proceeding ...")
    if shutil.which("bwrap"):
        print("> Bubblewrap already installed")
    else:
        subprocess.run(["sudo", "apt", "update"], check=True)
        subprocess.run(["sudo", "apt", "install", "bubblewrap", "-y"], check=True)

    print("> Bundling chrapt to ~/.local/bin/")
    finished_file = Path.home() / ".local" / "bin" / "chrapt"
    finished_file.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        "python3", "-m", "zipapp", "src/",
        "-o", str(finished_file),
        "-m", "main:main",
        "-p", "/usr/bin/env python3"
    ], check=True)

    finished_file.chmod(0o755)
    print(f"Chrapt was bundled succesfully to {finished_file}")

    bin_folder = Path.home() / ".chrapt" / "bin"
    bin_folder.mkdir(parents=True, exist_ok=True)

    with open(Path.home() / ".bashrc", "a", encoding="utf-8") as datei:
        datei.write("\n\n# Added by chrapt, can be removed after uninstall\nexport PATH=\"$HOME/.chrapt/bin:$PATH\"")

if __name__ == "__main__":
    chrapt_installer()
