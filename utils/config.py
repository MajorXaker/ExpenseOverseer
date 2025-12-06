import logging
import os
import pathlib

from dynaconf import Dynaconf

_configs_path = pathlib.Path(os.getcwd())
if not _configs_path.joinpath("settings.toml").exists():
    # launch from root directory (not app)
    _configs_path = _configs_path.joinpath("app")

settings = Dynaconf(
    env="default",
    environments=True,
    settings_files=["settings.toml", ".secrets.toml"],
    ROOT_PATH_FOR_DYNACONF=os.getcwd(),
)

log = logging.getLogger(__name__)

mpl_logger = logging.getLogger("matplotlib")
mpl_logger.setLevel(logging.INFO)