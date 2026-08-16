from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="LOON",
    settings_files=['settings.toml', '.secrets.toml'],
    merge_enabled=True,
)
