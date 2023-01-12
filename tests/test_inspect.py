from psql2py import inspect


pytest_plugins = ["pg_docker"]


def test_inspect_database(pg_database):
    result = inspect.inspect_database(pg_database.connection_kwargs())

    assert "public" in result.schemas
    public = result.schemas["public"]
    assert public.name == "public"
    assert "hero" in public.tables
    assert "kingdom" in public.tables
    hero = public.tables["hero"]
    assert hero.name == "hero"
    assert "hero_id" in hero.columns
    hero_id = hero.columns["hero_id"]
    assert hero_id == inspect.Column(
        name="hero_id",
        postgres_type="bigint",
        is_nullable=False,
    )

