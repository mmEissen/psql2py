from psql2py import generate
import click
import psycopg2


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
def main(daemon: bool, source: str, destination: str, db_host: str, db_port: str, db_name: str, db_user: str, db_password: str) -> None:
    db_options = {
        "dbname": db_name,
        "user": db_user,
        "password": db_password,
        "host": db_host,
        "port": db_port,
    }
    connection_factory = lambda: psycopg2.connect(**db_options)
    if daemon:
        generate.package_from_dir_continuous(source, destination, connection_factory)
    else:
        generate.package_from_dir(source, destination, connection_factory)


if __name__ == "__main__":
    main(auto_envvar_prefix="")
