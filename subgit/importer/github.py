import json
import logging
import subprocess
import os
import pysnooper


class GithubImport:
    def __init__(self, config_file_name=None, answer_yes=None):
        self.answer_yes = answer_yes

        if not config_file_name:
            self.subgit_config_file_name = ".subgit.yml"
            self.subgit_config_file_path = os.path.join(os.getcwd(), self.subgit_config_file_name)
        else:
            self.subgit_config_file_name = config_file_name
            self.subgit_config_file_path = os.path.join(os.getcwd(), config_file_name)

    def yes_no(self, question):
        print(question)

        if self.answer_yes:
            log.info(f"--yes flag set, automatically answer yes to question")
            return True

        answer = input("(y/n) << ")

        return answer.lower().startswith("y")

    @pysnooper.snoop()
    def import_github(self, namespace, answer_yes=None):
        """
        
        """
        out = subprocess.run([
                "gh",
                "repo",
                "list",
                f"{namespace}",
                "--json",
                "id,name,defaultBranchRef,sshUrl",
                "-L",
                "100"
            ],
            shell=False,
            capture_output=True,
        )
        data = json.loads(out.stdout)
        repos = {}
        mapped_data = {x["name"]: x for x in data}
        sorted_names = sorted([repo["name"] for repo in data])

        if os.path.exists(self.subgit_config_file_path):
            answer = self.yes_no(f"File: {self.subgit_config_file_path} already exists on disk, do you want to overwrite the file?")

            if not answer:
                print("Aborting import")
                return 1
            
        for repo_name in sorted_names:
            repo_data = mapped_data[repo_name]

            repos[repo_name] = {
                "revision": {
                    "branch": repo_data["defaultBranchRef"]["name"],
                },
                "url": repo_data["sshUrl"],
            }

        print(repos)