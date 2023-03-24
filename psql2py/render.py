from os import path
import pathlib
import jinja2

from psql2py import load



def package_from_statement_dir(statement_dir: load.StatementDir, output_path: str) -> None:
    output_path = path.join(output_path, statement_dir.name)
    pathlib.Path(output_path).mkdir(parents=True, exist_ok=True)
    with open(path.join(output_path, "__init__.py"), "w") as out_file:
        out_file.write(_render_module(statement_dir.statements))
    for sub_dir in statement_dir.sub_dirs:
        package_from_statement_dir(
            sub_dir,
            output_path,
        )


def _render_module(statements: list[load.Statement]) -> str:
    env = jinja2.Environment(
        loader=jinja2.PackageLoader("psql2py", "templates"),
    )
    template = env.get_template("module.py.jinja")
    return template.render({"statements": statements})
