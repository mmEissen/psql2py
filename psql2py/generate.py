from __future__ import annotations
from typing import Callable

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import traceback

import psycopg2.extensions
from psql2py import load, render, inspect


class _SqlDirChangeEventHandler(FileSystemEventHandler):
    def __init__(self, root_dir: str, target_dir: str, db_connection_factory: Callable[[],psycopg2.extensions.connection]) -> None:
        self.root_dir = root_dir
        self.target_dir = target_dir
        self.db_connection_factory = db_connection_factory

    def on_any_event(self, event: object) -> None:
        try:
            package_from_dir(self.root_dir, self.target_dir, self.db_connection_factory)
        except Exception:
            traceback.print_exc()


def package_from_dir_continuous(dirname: str, output_path: str, db_connection_factory: Callable[[],psycopg2.extensions.connection]) -> None:
    observer = Observer()
    event_handler = _SqlDirChangeEventHandler(dirname, output_path, db_connection_factory)
    observer.schedule(event_handler, dirname, recursive=True)
    observer.start()

    try:
        input("Press enter to stop")
    finally:
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
