from setuptools import setup

with open("README.md") as f:
    readme = f.read()

setup(
    name="sgit",
    version="0.1.0",
    description="CLI tool ",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Johan Andersson",
    author_email="johan@dynamist.se",
    maintainer="Johan Andersson",
    maintainer_email="johan@dynamist.se",
    license="Apache License 2.0",
    packages=["sgit"],
    url="http://github.com/dynamist/sgit",
    entry_points={
        "console_scripts": [
            "sgit = sgit.cli:cli_entrypoint",
            "git-sub = sgit.cli:cli_entrypoint",
        ]
    },
    install_requires=[
        "docopt>=0.6.2",
        "ruamel.yaml>=0.16.0",
        "gitpython>=3.1.0",
    ],
    python_requires=">=3.6",
    extras_require={
        "test": [
            "pytest",
            "pytest-mock",
            "mock",
        ],
        "dev": [
            "pylint",
        ],
    },
    classifiers=[
        # "Development Status :: 1 - Planning",
        # "Development Status :: 2 - Pre-Alpha",
        "Development Status :: 3 - Alpha",
        # "Development Status :: 4 - Beta",
        # "Development Status :: 5 - Production/Stable",
        # "Development Status :: 6 - Mature",
        # "Development Status :: 7 - Inactive",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: Apache Software License",
        "Environment :: Console",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Natural Language :: English",
    ],
)
