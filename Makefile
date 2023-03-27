all: create-local-test-repo subgit-init-and-pull change-local-test-repo subgit-pull clean

smoke-test-subgit-pull: create-local-test-repo subgit-init-and-pull change-local-test-repo subgit-pull clean

repo_name = subgit-smoke-test
repo_path = local/subgit-smoke-test.git/

create-local-test-repo:
	git init $(repo_path)
	touch $(repo_path)/README.md
	cd $(repo_path) && git add README.md && git commit -m "Initial commit"

subgit-init-and-pull:
	#
	# Initializing .subgit.yml file
	#
	subgit init $(repo_name) $(repo_path)
	#
	# Subgit pull test repo
	#
	subgit pull -y

change-local-test-repo:
	#
	# Touch new file and commit
	#
	cd $(repo_path) && touch example_file && git add example_file && git commit -m "example"

subgit-pull:
	#
	# This job will fail with the previous code
	# Pull changes made in local/subgit-smoke-test.git/
	#
	subgit pull -y

clean:
	#
	# -- Cleanup --
	# Remove .subgit.yml file
	#
	rm .subgit.yml
	#
	# Remove smoke test repo
	#
	rm -rf local/
	#
	# Remove test repo pulled with subgit
	#
	rm -rf $(repo_name)
