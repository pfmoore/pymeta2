import re
import attr
import cattr
from packaging.version import Version
from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet
from typing import Optional, List

# Setuptools adds License-File...?

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

cattr.register_structure_hook(Version, lambda d, _: Version(d))
cattr.register_structure_hook(Requirement, lambda d, _: Requirement(d))
cattr.register_structure_hook(SpecifierSet, lambda d, _: SpecifierSet(d))

@attr.s
class Metadata:
    metadata_version: Version = attr.ib()
    name: str = attr.ib()
    version: Version = attr.ib()
    dynamic: Optional[List[str]] = attr.ib(default=None, repr=False)
    platform: Optional[List[str]] = attr.ib(default=None, repr=False)
    supported_platform: Optional[List[str]] = attr.ib(default=None, repr=False)
    summary: Optional[str] = attr.ib(default=None)
    description: Optional[str] = attr.ib(default=None, repr=False)
    description_content_type: Optional[str] = attr.ib(default=None, repr=False)
    keywords: Optional[List[str]] = attr.ib(default=None, repr=False)
    home_page: Optional[str] = attr.ib(default=None, repr=False)
    download_url: Optional[str] = attr.ib(default=None, repr=False)
    author: Optional[str] = attr.ib(default=None, repr=False)
    author_email: Optional[str] = attr.ib(default=None, repr=False)
    maintainer: Optional[str] = attr.ib(default=None, repr=False)
    maintainer_email: Optional[str] = attr.ib(default=None, repr=False)
    license: Optional[str] = attr.ib(default=None, repr=False)
    classifier: Optional[List[str]] = attr.ib(default=None, repr=False)
    requires_dist: Optional[List[Requirement]] = attr.ib(default=None, repr=False)
    requires_python: Optional[SpecifierSet] = attr.ib(default=None, repr=False)
    requires_external: Optional[List[str]] = attr.ib(default=None, repr=False)
    project_url: Optional[List[str]] = attr.ib(default=None, repr=False)
    provides_extra: Optional[List[str]] = attr.ib(default=None, repr=False)
    provides_dist: Optional[List[str]] = attr.ib(default=None, repr=False)
    obsoletes_dist: Optional[List[str]] = attr.ib(default=None, repr=False)

    @classmethod
    def from_msg(cls, msg):
        d = msg_to_dict(msg)
        return cattr.structure(d, cls)
