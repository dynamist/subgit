import os
import shutil
import subgit
import uuid

from invoke import task
from pathlib import Path
from ruamel import yaml

# TODO: Base all files from where the tasks.py file is located

test_config = {
    "repos": [
        {
            "name": "pyk",
            "url": "git@github.com:Grokzen/pykwalify.git",
            "sparse": {
                "paths": [
                    "docs",
                    "tests",
                ],
            },
            "revision": {
                "branch": "master",
            },
        },
        {
            "name": "pykwalify",
            "url": "git@github.com:Grokzen/pykwalify.git",
            "sparse": {
                "paths": [
                    "docs",
                    "tests",
                ],
            },
            "clone_point": "pyk/docs",
            "revision": {
                "filter": "[0-9].[0-9].[0-9]",
                "order": "semver",
                "select": "last",
            },
        },
    ]
}


@task
def smoke_test(c):
    subgit.init_logging(5 if "DEBUG" in os.environ else 4)

    print(f"Running smoke tests")

    run_folder = str(uuid.uuid4())

    tests_folder = Path("./smoke_tests")

    # Check if the directory exists
    if not tests_folder.exists():
        # If it doesn't exist, create it
        tests_folder.mkdir(parents=True)

    run_tests_folder = tests_folder / run_folder

    if not run_tests_folder.exists():
        run_tests_folder.mkdir(parents=True)

    yaml_file = run_tests_folder / ".subgit.yml"

    if yaml_file.exists() is False:
        yaml_file.touch()

    with open(yaml_file, "w") as stream:
        yaml.dump(
            test_config,
            stream,
            indent=2,
            default_flow_style=False,
        )

    # Move into this run:s folder
    os.chdir(run_tests_folder)

    from subgit.core import SubGit

    core = SubGit(".subgit.yml")
    core.repo_status()
    core.pull(None)
    core.pull(["pyk"])
    core.pull(["pykwalify"])
    core.repo_status()
    core.fetch(None)
    core.fetch(["pyk"])
    core.fetch(["pykwalify"])
    core.clean(repo_names=None, recurse_into_dir=True, dry_run=True)
    core.clean(repo_names=["pyk"], recurse_into_dir=True, dry_run=True)
    core.clean(repo_names=["pykwalify"], recurse_into_dir=True, dry_run=True)


@task
def clean_smoke_tests(c):
    folder = Path("smoke_tests")

    if folder.exists() is False:
        print("Smoke test folder do not exists on disk")
        return

    print("Removing smoketest folder")
    shutil.rmtree(folder)
