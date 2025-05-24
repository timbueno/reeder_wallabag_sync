from setuptools import setup, find_packages

# Read development requirements
with open("requirements-dev.txt") as f:
    dev_requirements = f.read().splitlines()

setup(
    name="wallabag_sync",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": dev_requirements,
    },
    entry_points={
        "console_scripts": [
            "wallabag-sync=wallabag_sync.cli:main",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool to synchronize a JSON feed with Wallabag",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/wallabag_sync",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
) 