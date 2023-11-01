from distutils.core import setup
from pathlib import Path

from setuptools import find_packages

try:
    from Rankings.version import __version__
except ModuleNotFoundError:
    # I think we always end up here unless we have every necessary package installed (which we don't want to do)
    exec(Path("MongoBase/version.py").open().read())

setup(
    name="MongoBase",
    version=__version__,  # type: ignore
    packages=find_packages(),
    package_data={p: ["*"] for p in find_packages()},
    url="",
    license="",
    install_requires=["pydantic<2.0", "fastapi", "click", "uvicorn", "loguru", "motor", "mongomock_motor", "MongoBase"],
    python_requires=">=3.10.0",
    command_options={
        "build_sphinx": {"version": ("setup.py", __version__), "source_dir": ("setup.py", "docs")}  # type: ignore
    },
    author="Andy.Bryson",
    author_email="andy.bryson@bartechnologies.uk",
    description="A set of base documents and functionality for interacting with our MongoDB",
)
