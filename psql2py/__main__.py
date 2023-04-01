import os
from psql2py import generate
import click
import psycopg2


class InvalidSourceDir(Exception):
    pass


@click.command
@click.argument("source", type=click.Path(exists=True))
@click.argument("destination", type=click.Path(exists=True))
@click.option("--db-host", type=click.STRING, default="localhost")
@click.option("--db-port", type=click.INT, default=5432)
@click.option("--db-name", type=click.STRING, default="postgres")
@click.option("--db-user", type=click.STRING, default="postgres")
@click.option("--db-password", type=click.STRING, default="postgres")
@click.option(
    "-d", 
    "--daemon", 
    is_flag=True, 
    default=False, 
    show_default=True, 
    help=(
        "Run forever, watching the source directory for changes and regenerating the "
        "modules on any change."
    )
)
@click.option(
    "--use-subdir", 
    is_flag=True, 
    default=False, 
    show_default=True, 
    help=(
        "If set, the source directory should only contain one subdir. This subdir is used "
        "as the source for the packages."
    )
)
def main(use_subdir: bool, daemon: bool, source: str, destination: str, db_host: str, db_port: str, db_name: str, db_user: str, db_password: str) -> None:
    db_options = {
        "dbname": db_name,
        "user": db_user,
        "password": db_password,
        "host": db_host,
        "port": db_port,
    }
    print(db_options)
    connection_factory = lambda: psycopg2.connect(**db_options)

    if use_subdir:
        files = os.listdir(source)
        dirs = [file_ for file_ in files if os.path.isdir(os.path.join(source, file_))]
        if len(dirs) != 1:
            raise InvalidSourceDir()
        source = os.path.join(source, dirs[0])

    if daemon:
        generate.package_from_dir_continuous(source, destination, connection_factory)
    else:
        generate.package_from_dir(source, destination, connection_factory)


if __name__ == "__main__":
    main(auto_envvar_prefix="PSQL2PY")
