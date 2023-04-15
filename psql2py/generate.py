from __future__ import annotations
import time
from typing import Callable

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
import traceback
import checksumdir


import psycopg2.extensions
from psql2py import load, render, inspect


class _SqlDirChangeEventHandler(FileSystemEventHandler):
    def __init__(self, root_dir: str, target_dir: str, db_connection_factory: Callable[[],psycopg2.extensions.connection]) -> None:
        self.root_dir = root_dir
        self.target_dir = target_dir
        self.db_connection_factory = db_connection_factory
        self._most_recent_checksum = checksumdir.dirhash(self.root_dir)

    def on_any_event(self, event: FileSystemEvent) -> None:
        if event == "opened":
            return
        new_checksum = checksumdir.dirhash(self.root_dir)
        if new_checksum == self._most_recent_checksum:
            return
        self._most_recent_checksum = new_checksum
        print(f"Detected {event.event_type} on {event.src_path}")
        try:
            package_from_dir(self.root_dir, self.target_dir, self.db_connection_factory)
        except Exception:
            traceback.print_exc()


def package_from_dir_continuous(dirname: str, output_path: str, db_connection_factory: Callable[[],psycopg2.extensions.connection]) -> None:
    print("Generating from initial state...")
    package_from_dir(dirname, output_path, db_connection_factory)

    print("Starting filesystem observer...")
    observer = Observer()
    event_handler = _SqlDirChangeEventHandler(dirname, output_path, db_connection_factory)
    observer.schedule(event_handler, dirname, recursive=True)
    observer.start()

    print("Press Ctrl-C to stop.")
    try:
        while observer.is_alive():
            time.sleep(0.1)
    finally:
        print("Stopping filesystem observer...")
        observer.stop()
        observer.join()


def package_from_dir(dirname: str, output_path: str, db_connection_factory: Callable[[],psycopg2.extensions.connection]) -> None:
    statement_dir = load.load_dir_recursive(dirname)
    db_connection = db_connection_factory()
    inference_func = lambda statement: inspect.infer_types(statement, db_connection)
    try:
        package_or_module = statement_dir.to_package_or_module(inference_func)
    finally:
        db_connection.close()
    render.package_or_module(package_or_module, output_path)
