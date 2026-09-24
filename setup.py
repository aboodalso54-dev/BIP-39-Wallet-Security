"""Setup script for DevForge 2.0.

Intelligent Development Environment - Making the Impossible Possible.
"""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="devforge",
    version="2.0.0",
    author="DevForge Team",
    author_email="devforge@example.com",
    description=(
        "Intelligent Development Environment - orchestrates dev tools, "
        "predicts bugs, translates code, and auto-fixes issues."
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/devforge/devforge",
    packages=find_packages(exclude=("tests", "tests.*")),
    python_requires=">=3.9",
    install_requires=[
        "requests>=2.28.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "ruff>=0.1.0",
            "mypy>=1.0.0",
        ],
        "android": [
            "androguard>=3.4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "devforge = devforge.cli_v2:main",
            "devforge2 = devforge.cli_v2:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Build Tools",
    ],
    keywords="devtools cli automation ai code-generation translation",
)