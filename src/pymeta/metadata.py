import re
import attrs
from packaging.version import Version
from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet
from typing import Optional, List
from functools import partial

optional = partial(attrs.field, default=None, repr=False)

# Setuptools adds License-File...?

@attrs.frozen()
class Metadata_1_0:
    metadata_version: Version = attrs.field(converter=Version)
    name: str # More restricted from 2.1 onwards
    version: Version = attrs.field(converter=Version)
    platform: Optional[List[str]] = optional()
    summary: Optional[str] = None
    description: Optional[str] = optional() # Can be in message body from 2.1
    keywords: Optional[List[str]] = optional()
    home_page: Optional[str] = optional()
    author: Optional[str] = optional()
    author_email: Optional[str] = optional()
    license: Optional[str] = optional()


@attrs.frozen()
class Metadata_1_1:
    supported_platform: Optional[List[str]] = optional()
    download_url: Optional[str] = optional()
    classifier: Optional[List[str]] = optional()

@attrs.frozen()
class Metadata_1_2:
    maintainer: Optional[str] = optional()
    maintainer_email: Optional[str] = optional()
    # requires_dist, requires_external, provides_dist, obsoletes_dist spec relaxed in 2.1
    requires_dist: Optional[List[Requirement]] = optional(converter=lambda lst: None if lst is None else [Requirement(x) for x in lst])
    requires_python: Optional[SpecifierSet] = optional(converter=lambda x: None if x is None else SpecifierSet)
    requires_external: Optional[List[str]] = optional()
    project_url: Optional[List[str]] = optional()
    provides_extra: Optional[List[str]] = optional()
    provides_dist: Optional[List[str]] = optional()
    obsoletes_dist: Optional[List[str]] = optional()

@attrs.frozen()
class Metadata_2_1:
    description_content_type: Optional[str] = optional()

@attrs.frozen()
class Metadata_2_2:
    dynamic: Optional[List[str]] = optional()


fields = [
    # (name, multiple_use, introduced_in)
    ("Metadata-Version", False, (1, 0)),
    ("Name", False, (1, 0)),
    ("Version", False, (1, 0)),
    ("Dynamic", True, (2, 2)),
    ("Platform", True, (1, 0)),
    ("Supported-Platform", True, (1, 1)),
    ("Summary", False, (1, 0)),
    ("Description", False, (1, 0)),
    ("Description-Content-Type", False, (2, 1)),
    ("Keywords", False, (1, 0)),
    ("Home-page", False, (1, 0)),
    ("Download-URL", False, (1, 1)),
    ("Author", False, (1, 0)),
    ("Author-email", False, (1, 0)),
    ("Maintainer", False, (1, 2)),
    ("Maintainer-email", False, (1, 2)),
    ("License", False, (1, 0)),
    ("Classifier", True, (1, 1)),
    ("Requires-Dist", True, (1, 2)),
    ("Requires-Python", False, (1, 2)),
    ("Requires-External", True, (1, 2)),
    ("Project-URL", True, (1, 2)),
    ("Provides-Extra", True, (2, 1)),
    ("Provides-Dist", True, (1, 2)),
    ("Obsoletes-Dist", True, (1, 2)),
]

known_versions = {"1.0", "1.1", "1.2", "2.1", "2.2"}

def msg_to_dict(msg):
    meta_ver = msg["Metadata-Version"]
    if meta_ver not in known_versions:
        raise ValueError(f"Unknown metadata version: {meta_ver}")
    meta_ver = tuple(int(n) for n in meta_ver.split("."))
    result = {}
    for name, multi, introduced in fields:
        # Skip fields that were introduced in later metadata versions
        if meta_ver < introduced:
            continue
        attr_name = name.lower().replace("-", "_")
        getter = msg.get_all if multi else msg.get
        value = getter(name)
        # Updated in 2.2 to use commas, not spaces
        # We should split on either, for compatibility
        if name == "Keywords" and value is not None:
            value = re.split(r'\s*[ ,]\s*', value.strip())
        result[attr_name] = value
    # If both Description and body are present, which one
    # takes priority? The spec isn't 100% clear, but
    # we assume Description.
    # We check the value, rather than existence, so that a body
    # overrides a specified but empty value.
    if not result.get("description"):
        body = msg.get_payload()
        if body:
            result["description"] = body

    return result

@attrs.frozen()
class Metadata:
    metadata_version: Version = attrs.field(converter=Version)
    name: str
    version: Version = attrs.field(converter=Version)
    dynamic: Optional[List[str]] = optional()
    platform: Optional[List[str]] = optional()
    supported_platform: Optional[List[str]] = optional()
    summary: Optional[str] = None
    description: Optional[str] = optional()
    description_content_type: Optional[str] = optional()
    keywords: Optional[List[str]] = optional()
    home_page: Optional[str] = optional()
    download_url: Optional[str] = optional()
    author: Optional[str] = optional()
    author_email: Optional[str] = optional()
    maintainer: Optional[str] = optional()
    maintainer_email: Optional[str] = optional()
    license: Optional[str] = optional()
    classifier: Optional[List[str]] = optional()
    requires_dist: Optional[List[Requirement]] = optional(converter=lambda lst: None if lst is None else [Requirement(x) for x in lst])
    requires_python: Optional[SpecifierSet] = optional(converter=lambda x: None if x is None else SpecifierSet)
    requires_external: Optional[List[str]] = optional()
    project_url: Optional[List[str]] = optional()
    provides_extra: Optional[List[str]] = optional()
    provides_dist: Optional[List[str]] = optional()
    obsoletes_dist: Optional[List[str]] = optional()

    @classmethod
    def from_msg(cls, msg):
        d = msg_to_dict(msg)
        return cls(**d)

    @classmethod
    def from_pyproject(cls, project):
        """Construct metadata from the [project] section of pyproject.toml"""
        kw = {}
        kw["name"] = project["name"]
        kw["version"] = project.get("version") # TODO: Not optional in metadata!
        kw["summary"] = project.get("description")
        readme = project.get("readme")
        # TODO:
        # filename, or table with file/text and content-type and charset
        kw["description"] = ...
        kw["requires_python"] = project.get("requires-python")
        license = project.get("license")
        # TODO:
        # table with file or text
        kw["license"] = ...
        project.get("authors")
        project.get("maintainers")
        kw["keywords"] = ",".join(project.get("keywords")) # ish...
        kw["classifiers"] = project.get("classifiers")
        if "urls" in project:
            kw["urls"] = [f"{name}, {url}" for (name, url) in project["urls"].items()]
        # TODO: Entry points
        # TODO: dependencies, optional-dependencies
        # TODO: dynamic
