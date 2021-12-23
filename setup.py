import os
import pathlib
import pkg_resources
from setuptools import setup, find_packages, Command

with pathlib.Path("requirements.txt").open(encoding="utf-8") as requirements:
    install_reqs = [
        str(require) for require in pkg_resources.parse_requirements(requirements)
    ]

with pathlib.Path("requirements-dev.txt").open(encoding="utf-8") as requirements_dev:
    develop_reqs = [
        str(require) for require in pkg_resources.parse_requirements(requirements_dev)
    ]


class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""

    CLEAN_FILES = "./build ./dist ./src/*.egg-info"
    PYTHON_CACHE = "$(find . -path ./.env -prune -name __pycache__ | xargs)"

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system(f"rm -vrf {self.CLEAN_FILES} {self.PYTHON_CACHE}")


# Reference links:
# - https://packaging.python.org/guides/distributing-packages-using-setuptools/
# - https://github.com/pypa/sampleproject
setup(
    name="git_search",
    version="0.1",
    description="Helpful command to search code snippet from gitlab",
    url="https://github.com/nguyen-ngoc-thach/git-search-command",
    author="Nguyễn Ngọc Thạch",
    author_email="thachnguyen1989@gmail.com",
    # For a list of valid classifiers : https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="gitlab, search, command line, python",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    # https://packaging.python.org/guides/distributing-packages-using-setuptools/#python-requires
    python_requires=">=3.6, <4",
    install_requires=install_reqs,
    extras_require={"develop": develop_reqs},
    entry_points={
        "console_scripts": [
            "gitsearch=git_search:search_main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/nguyen-ngoc-thach/git-search-command/issues",
        "Source": "https://github.com/nguyen-ngoc-thach/git-search-command",
    },
    cmdclass={"clean": CleanCommand},
)
