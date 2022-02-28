import os
import shutil
from setuptools import setup, find_packages, Command


class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""

    CLEAN_DIR_NAMES = ("build", "dist", "__pycache__", "git_search_command.egg-info")
    TOP_DIR = "."
    EXCLUDE_DIRS = ".env"

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        for root, dirs, _files in os.walk(self.TOP_DIR, topdown=True):
            dirs[:] = [d for d in dirs if d not in self.EXCLUDE_DIRS]
            dirs_should_removed = set(dirs) & set(self.CLEAN_DIR_NAMES)
            for name in dirs_should_removed:
                dir_path = os.path.join(root, name)
                try:
                    shutil.rmtree(dir_path)
                    print(f'Has removed "{dir_path}".')
                except OSError as err:
                    print(f'Cannot remove "{dir_path}".')
                    print(f"[Error] {err}")


# Reference links:
# - https://packaging.python.org/guides/distributing-packages-using-setuptools/
# - https://github.com/pypa/sampleproject
setup(
    name="git_search_command",
    use_scm_version=True,
    description="A simple tool to search the expression in the project scope for GitLab and GitHub repositories.",
    url="https://github.com/nguyen-ngoc-thach/git-search-command",
    author="Nguyen Ngoc Thach",
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
    keywords="gitlab, search, command line, python, git, github",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    # https://packaging.python.org/guides/distributing-packages-using-setuptools/#python-requires
    python_requires=">=3.6, <4",
    install_requires=[
        "requests>=2.26.0",
        "rx>=3.2.0",
        "click>=8.0.3",
        "python-dotenv>=0.19.2",
    ],
    extras_require={
        "develop": ["black>=21.12b0", "pre-commit>=2.16.0", "pylint>=2.12.2"]
    },
    entry_points={"console_scripts": ["gsc=gsc:main"]},
    project_urls={
        "Bug Reports": "https://github.com/nguyen-ngoc-thach/git-search-command/issues",
        "Source": "https://github.com/nguyen-ngoc-thach/git-search-command",
    },
    cmdclass={"clean": CleanCommand},
)
