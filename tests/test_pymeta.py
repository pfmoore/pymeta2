from email import message_from_string
from pymeta import Metadata
from packaging.version import Version

TEST_DATA = """\
Metadata-Version: 2.1
Name: editables
Version: 0.2
Summary: Editable installations
Home-page: https://github.com/pfmoore/editables
Author: Paul Moore
Author-email: p.f.moore@gmail.com
Maintainer: Paul Moore
Maintainer-email: p.f.moore@gmail.com
License: MIT
Project-URL: Source, https://github.com/pfmoore/editables
Project-URL: Tracker, https://github.com/pfmoore/editables/issues
Keywords: packaging,editables
Platform: any
Classifier: Development Status :: 5 - Production/Stable
Classifier: Intended Audience :: Developers
Classifier: License :: OSI Approved :: MIT License
Classifier: Programming Language :: Python :: 3
Classifier: Programming Language :: Python :: 3 :: Only
Classifier: Programming Language :: Python :: 3.5
Classifier: Programming Language :: Python :: 3.6
Classifier: Programming Language :: Python :: 3.7
Classifier: Programming Language :: Python :: 3.8
Classifier: Programming Language :: Python :: Implementation :: CPython
Classifier: Programming Language :: Python :: Implementation :: PyPy
Classifier: Topic :: Software Development :: Libraries
Classifier: Topic :: Utilities
Requires-Python: >=3.5
Description-Content-Type: text/markdown

# A Python library for creating "editable wheels"

This library supports the building of wheels which, when installed, will
expose packages in a local directory on `sys.path` in "editable mode". In
other words, changes to the package source will be  reflected in the package
visible to Python, without needing a reinstall.

## Usage

Suppose you want to build a wheel for your project `foo`. Your project is
located in the directory `/path/to/foo`. Under that directory, you have a
`src` directory containing your project, which is a package called `foo`
and a Python module called `bar.py`. So your directory structure looks like
this:

```
/path/to/foo
|
+-- src
|   +-- foo
|   |   +-- __init__.py
|   +-- bar.py
|
+-- setup.py
+-- other files
```

Build your wheel as follows:

```python
from editables import EditableProject

my_project = EditableProject("foo", "/path/to/foo")
my_project.map("foo", "src/foo")
my_project.map("bar", "src/bar.py")

# Build a wheel however you prefer...
wheel = BuildAWheel()

# Add files to the wheel
for name, content in my_project.files():
    wheel.add_file(name, content)

# Add any runtime dependencies to the wheel
for dep in my_project.dependencies():
    wheel.metadata.dependencies.add(dep)
```

The resulting wheel will, when installed, put packages `foo` and `bar` on
`sys.path` so that editing the original source will take effect without needing
a reinstall (i.e., as "editable" packages).

Exposing individual packages like this requires an import hook, which is itself
provided by the `editables` package. That's why you need to add a (runtime)
dependency to the wheel metadata, so that the installer will install the hook
code as well. The dependencies are provided via an API call so that if, at
some future point, the hook code gets moved to its own project, callers will
not need to change.

If you don't need to expose individual packages like this, but are happy to
put the whole of the `src` directory onto `sys.path`, you can do this using
`my_project.add_to_path("src")`. If you *only* use `add_to_path`, and not
`map`, then no runtime dependency will be required (although you should not
rely on this, you should still call `dependencies` to allow for future
changes in implementation).

Using `add_to_path` is the only reliable way of supporting implicit namespace
packages - the mechanism used in `map` does not handle them correctly.

Note that this project doesn't build wheels directly. That's the responsibility
of the calling code.

## Python Compatibility

This project supports the same versions of Python as pip does. Currently
that is Python 3.6 and later, and PyPy3 (although we don't test against
PyPy).
"""

def test_simple():
    msg = message_from_string(TEST_DATA)
    meta = Metadata.from_msg(msg)
    assert meta.name == "editables", "Parsing returned incorrect name"
    assert meta.version == Version("0.2"), "Incorrect version"
