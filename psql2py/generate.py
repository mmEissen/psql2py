from __future__ import annotations

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import traceback

from psql2py import load, render, inspect

COLUMNS = "\nCOLUMNS:\n"


class _SqlDirChangeEventHandler(FileSystemEventHandler):
    def __init__(self, root_dir: str, target_dir: str) -> None:
        self.root_dir = root_dir
        self.target_dir = target_dir

    def on_any_event(self, event: object) -> None:
        try:
            package_from_dir(self.root_dir, self.target_dir)
        except Exception:
            traceback.print_exc()


def package_from_dir_continuous(dirname: str, output_path: str) -> None:
    observer = Observer()
    event_handler = _SqlDirChangeEventHandler(dirname, output_path)
    observer.schedule(event_handler, dirname, recursive=True)
    observer.start()

    try:
        input("Press enter to stop")
    finally:
        observer.stop()
        observer.join()


def package_from_dir(dirname: str, output_path: str) -> None:
    statement_dir = load.load_dir_recursive(dirname)
    #shutil.rmtree(path.join(output_path, statement_dir.name))
    render.package_from_statement_dir(statement_dir, output_path)

