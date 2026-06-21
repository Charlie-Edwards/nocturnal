import os
from pathlib import Path
from urllib.parse import urlparse
import configparser
import getpass
import requests
import subprocess

# nocturnal 2026 - using the web offline

CONFIG_PATH = "config.conf"

config = configparser.ConfigParser()
config.read("config.conf")

bookmarks = []


def updbookmarks():
    global bookmarks

    config.read("config.conf")

    if "BOOKMARKS" in config and "sites" in config["BOOKMARKS"]:
        bookmarks = [
            b.strip()
            for b in config["BOOKMARKS"]["sites"].split(", ")
            if b.strip()
        ]
    else:
        bookmarks = []


lastupdated = config["LASTUPDATED"]["time"] if "LASTUPDATED" in config else "never"

user = getpass.getuser()

path = Path.cwd()
base = Path.home()

relative = path.relative_to(base)
print(relative)

info = ""
cmd = ""


def urlchecker(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def helpcmd():
    global info
    global cmd
    os.system("cls")
    print(f"""╭───────────────────────────────────────────────────╮
│ + Nocturnal 2026 - browse the web offline  (help) │
╰───────────────────────────────────────────────────╯
""") # tui layout inspired by codex
    print(f"""Type a url in the text field below to use it offline
Use /update to update your websites and nocturnal below

Type /back to go back to the menu\n
""")
    cmd = input(f"{user}@nocturnal> ")
    prompt()


def showbookmarks():
    global info
    global cmd
    print(f"""╭───────────────────────────────────────────────────╮
│ + Nocturnal 2026 - browse the web offline         │
│                                                   │""")
    for bookmark in range(len(bookmarks)):
        print(f"""│ {bookmarks[bookmark]:<49} │""")
    print("""╰───────────────────────────────────────────────────╯
""")
    info = "These are your bookmarks, do /update to download them"
    cmd = input(f"{user}@nocturnal")
    prompt()


def updatebookmarks():
    global info
    print(f"Updating {len(bookmarks)} local sites...")
    if len(bookmarks) == 0:
        if not os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "w") as f:
                f.write("[BOOKMARKS]\nsites=\n[LASTUPDATED]\ntime=never\n")
        else:
            open(CONFIG_PATH)
        info = f"No bookmarks to update, add a bookmark by pasting the websites url into the text field!"
        main()
    else:
        for bookmark in bookmarks:
            parsed = urlparse(bookmark)
            domain = parsed.netloc
            path = parsed.path.strip("/")
            if path:
                filename = f"bookmarks/{domain}/{path}.html"
            else:
                filename = f"bookmarks/{domain}/index.html"
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, "w", encoding="utf-8") as f:
                f.write(requests.get(bookmark).text)
        subprocess.run("git stash && git pull", shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        main()


def tuiheader():
    print(f"""╭───────────────────────────────────────────────────╮
│ + Nocturnal 2026 - browse the web offline  (main) │
│                                                   │
│ Bookmarks: {len(bookmarks):<27} /bookmarks │
│ last updated: {lastupdated:<27} /update │
│ /help, /update, url             - Charlie Edwards │
╰───────────────────────────────────────────────────╯
""") # tui layout inspired by codex


def main():
    global info
    global cmd
    updbookmarks()
    os.system("cls")
    tuiheader()
    print(f"{info}\n")
    cmd = input(f"{user}@nocturnal> ")
    prompt()


def prompt():
    global cmd
    global info
    if cmd == "":
        info = ""
        os.system("cls")
        main()
    elif cmd[0] == "/":
        if cmd == "/help":
            os.system("cls")
            helpcmd()
        elif cmd == "/bookmarks":
            os.system("cls")
            showbookmarks()
        elif cmd == "/update":
            os.system("cls")
            updatebookmarks()
        elif cmd == "/back":
            os.system("cls")
            main()
        else:
            info = f"Unknown command: {cmd}"
            main()
    else:
        if urlchecker(cmd):
        
            if cmd not in bookmarks:
                bookmarks.append(f"{cmd}")

            if "BOOKMARKS" not in config:
                config["BOOKMARKS"] = {}

            config["BOOKMARKS"]["sites"] = ", ".join(bookmarks)

            with open("config.conf", "w") as f:
                config.write(f)

            info = f"Added bookmark: {cmd}"
        else:
            pass
        info = ""
        os.system("cls")
        main()


main()
