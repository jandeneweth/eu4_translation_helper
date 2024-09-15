import dataclasses
import json
import logging
import pathlib

from .defines import EU4TH_DIR, EXCEL_FILENAME

_CONFIG_FILENAME = "config.json"
_KNOWN_PROJECTS_FILE = EU4TH_DIR / "known_projects.json"


@dataclasses.dataclass
class KnownProjects:
    project_directories: list[pathlib.Path] = dataclasses.field(default_factory=list)


def save_known_projects(projects: KnownProjects):
    logging.info(f"Saving known projects to {str(_KNOWN_PROJECTS_FILE)!r}")
    projects_dict = {
        "projects": [str(dirpath) for dirpath in projects.project_directories],
    }
    _KNOWN_PROJECTS_FILE.parent.mkdir(exist_ok=True, parents=True)
    with open(_KNOWN_PROJECTS_FILE, "w", encoding="utf-8-sig") as fh:
        json.dump(projects_dict, fh, indent=2)


def load_known_projects() -> KnownProjects:
    if not _KNOWN_PROJECTS_FILE.exists():
        return KnownProjects()
    try:
        with open(_KNOWN_PROJECTS_FILE, "r", encoding="utf-8-sig") as fh:
            content = fh.read()
    except IOError:
        logging.info("Projects data does not yet exist")
        return KnownProjects()
    try:
        projects_dict = json.loads(content)
    except json.JSONDecodeError as e:
        logging.warning(f"Error loading projects data: {e}")
        return KnownProjects()
    try:
        return KnownProjects(
            project_directories=[pathlib.Path(strpath) for strpath in projects_dict["projects"]],
        )
    except ValueError as e:
        logging.warning(f"Error loading projects data: {e}")
        return KnownProjects()


def add_known_project(project_directory: pathlib.Path):
    if not project_directory.exists():
        raise RuntimeError(f"Directory does not exist: {str(project_directory)!r}")
    known_projects = load_known_projects()
    if project_directory in known_projects.project_directories:
        raise RuntimeError(f"Project is already known: {str(project_directory)!r}")
    known_projects.project_directories.append(project_directory.resolve())
    save_known_projects(projects=known_projects)


def remove_known_project(project_directory: pathlib.Path):
    known_projects = load_known_projects()
    try:
        known_projects.project_directories.remove(project_directory.resolve())
    except ValueError as e:
        raise RuntimeError(
            f"Project not known: {str(project_directory)!r}. "
            f"Known projects: {', '.join(repr(str(p)) for p in known_projects.project_directories)}"
        ) from e
    save_known_projects(projects=known_projects)


@dataclasses.dataclass
class Project:
    project_directory: pathlib.Path
    project_name: str = "<Unknown>"
    reference_language: str = "english"
    reference_directory: pathlib.Path | None = None
    translation_language: str = ""
    translation_outfile: pathlib.Path | None = None
    exclude_references: list = dataclasses.field(default_factory=list)

    @property
    def translations_table(self) -> pathlib.Path:
        return self.project_directory / EXCEL_FILENAME


def save_project(project: Project):
    logging.info(f"Saving project {project.project_name!r} to {str(project.project_directory)!r}")
    config_dict = {
        "project_name": project.project_name,
        "reference_directory": str(project.reference_directory) if project.reference_directory else None,
        "reference_language": project.reference_language,
        "translation_filepath": str(project.translation_outfile) if project.translation_outfile else None,
        "translation_language": project.translation_language,
        "exclude_references": project.exclude_references,
    }
    project.project_directory.mkdir(exist_ok=True, parents=True)
    with open(project.project_directory / _CONFIG_FILENAME, "w", encoding="utf-8-sig") as fh:
        json.dump(config_dict, fh, indent=2)


def load_project(project_directory: pathlib.Path) -> Project:
    logging.info(f"Loading project from {str(project_directory)!r}")
    if not project_directory.exists():
        project_directory.mkdir(parents=True, exist_ok=True)
    if not project_directory.is_dir():
        raise RuntimeError("Project directory path must point to a directory, if it already exists")
    try:
        with open(project_directory / _CONFIG_FILENAME, "r", encoding="utf-8-sig") as fh:
            content = fh.read()
    except IOError:
        logging.info("Config does not yet exist")
        return Project(project_directory=project_directory)
    try:
        config_dict = json.loads(content)
    except json.JSONDecodeError as e:
        logging.warning(f"Error loading config: {e}")
        return Project(project_directory=project_directory)
    try:
        return Project(
            project_name=config_dict["project_name"],
            project_directory=project_directory,
            reference_directory=(
                pathlib.Path(config_dict["reference_directory"]) if config_dict["reference_directory"] else None
            ),
            reference_language=config_dict["reference_language"],
            translation_outfile=(
                pathlib.Path(config_dict["translation_filepath"]) if config_dict["translation_filepath"] else None
            ),
            translation_language=config_dict["translation_language"],
            exclude_references=config_dict.get("exclude_references", []),
        )
    except ValueError as e:
        logging.warning(f"Error loading config: {e}")
        return Project(project_directory=project_directory)
