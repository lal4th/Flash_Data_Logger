"""
Flash Data Logger v0.9 - Setup Script
Standalone package for PicoScope data acquisition with math channel functionality.
"""

from setuptools import setup, find_packages
import os
from pathlib import Path

# Read the README file with robust encoding handling
this_directory = Path(__file__).parent
readme_path = this_directory / "README.md"
try:
    long_description = readme_path.read_text(encoding="utf-8")
except UnicodeDecodeError:
    try:
        # Handle BOM/UTF-16 scenarios gracefully
        long_description = readme_path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        # Fallback to latin-1 to avoid install-time failures on some systems
        long_description = readme_path.read_text(encoding="latin-1")

# Read requirements
requirements = []
with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="flash-data-logger",
    version="0.9.0",
    author="Flash Data Logger Team",
    author_email="",
    description="Production-ready PC application for high-performance real-time data acquisition from PicoScope oscilloscopes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lal4th/Flash_Data_Logger",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Physics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "flash-data-logger=app.main:run",
            "fdl=app.main:run",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.pdf"],
    },
    keywords="picoscope, oscilloscope, data-acquisition, real-time, streaming, math-channels, csv-export",
    project_urls={
        "Bug Reports": "https://github.com/lal4th/Flash_Data_Logger/issues",
        "Source": "https://github.com/lal4th/Flash_Data_Logger",
        "Documentation": "https://github.com/lal4th/Flash_Data_Logger/blob/main/README.md",
    },
)
