from psql2py import generate
import click


@click.command
@click.argument("in-dir")
@click.argument("out-file")
def main(in_dir: str, out_file: str) -> None:
    generate.package_from_dir_continuous(in_dir, out_file)


if __name__ == "__main__":
    main()