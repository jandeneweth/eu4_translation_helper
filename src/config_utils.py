import dataclasses
import json
import logging
import pathlib

from .defines import CONFIG_PATH, DEFAULT_TRANSLATIONS_FILEPATH, EU4TH_DIR


@dataclasses.dataclass
class Config:
    reference_directory: pathlib.Path = pathlib.Path("")
    translation_filepath: pathlib.Path = DEFAULT_TRANSLATIONS_FILEPATH
    translation_language: str = ""
    reference_language: str = "english"
    tool_dir: pathlib.Path = pathlib.Path(EU4TH_DIR)
    exclude_references: list = dataclasses.field(default_factory=list)


def save_config(config: Config):
    logging.info(f"Saving config to {str(CONFIG_PATH)!r}")
    config_dict = {
        "reference_directory": config.reference_directory,
        "reference_language": config.reference_language,
        "translation_filepath": config.translation_filepath,
        "translation_language": config.translation_language,
    }
    CONFIG_PATH.parent.mkdir(exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as fh:
        json.dump(config_dict, fh, indent=2)


def load_config() -> Config:
    logging.info(f"Loading config from {str(CONFIG_PATH)!r}")
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as fh:
            content = fh.read()
    except IOError:
        logging.info("Config does not yet exist")
        return Config()
    try:
        config_dict = json.loads(content)
    except json.JSONDecodeError as e:
        logging.warning(f"Error loading config: {e}")
    try:
        return Config(
            reference_directory=pathlib.Path(config_dict["reference_directory"]),
            reference_language=config_dict["reference_language"],
            translation_filepath=pathlib.Path(config_dict["translation_filepath"]),
            translation_language=config_dict["translation_language"],
        )
    except ValueError as e:
        logging.warning(f"Error loading config: {e}")
