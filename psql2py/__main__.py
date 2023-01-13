from psql2py import generate, config
import click


@click.command
@click.option(
    "--conf-file",
    type=click.Path(exists=True, dir_okay=False),
    default="pyproject.toml",
)
def main(conf_file: str) -> None:
    config.load_config(conf_file)
    generate.package_from_dir_continuous(
        config.config().source_directory, config.config().output_directory
    )


if __name__ == "__main__":
    main()
