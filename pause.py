from pathlib import Path

FILE = Path("state.txt")

if not FILE.exists():
    FILE.write_text("ACTIVE")


def is_paused():

    return FILE.read_text().strip() == "PAUSED"


def pause():

    FILE.write_text("PAUSED")


def resume():

    FILE.write_text("ACTIVE")


def status():

    return FILE.read_text().strip()