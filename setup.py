"""
setup.py
Package setup configuration
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("backend/requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="shopping-trend-radar",
    version="1.0.0",
    author="Shopping Trend Radar Team",
    author_email="contact@trendradar.com",
    description="AI-powered shopping trend analysis across multiple platforms",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/samirasamrose/shopping-trend-radar",
    project_urls={
        "Bug Tracker": "https://github.com/samirasamrose/shopping-trend-radar/issues",
        "Documentation": "https://github.com/samirasamrose/shopping-trend-radar/docs",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    package_dir={"": "backend"},
    packages=find_packages(where="backend"),
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.7.0",
            "flake8>=6.1.0",
            "mypy>=1.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "trend-radar=app.main:main",
        ],
    },
)
