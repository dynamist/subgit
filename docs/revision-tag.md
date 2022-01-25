# Revision: tag

If you want to use the more specialized and advanced option for parsing and selecting a specific tag from a git repo then you should use the tag revision option.

This is the following syntax and extra options. More detailed examples is further down in this document.

```yaml
repos:
  pykwalify:
    clone-url: git@github.com:Grokzen/pykwalify.git
    revision:
      tag: latest

      # Pre-processes the tags before matching and removes any that we do not want
      # This step runs before clean step.
      # Multiple regex values is supported but it will stop parsing at first match and remove it
      tag-filter-regex:
        - "([0-9].[0-9].[0-9])"

      # Pre-processes the tags before selection step. Create a regex with a group that you want
      # to extract the semver data from. Multiple regex values is supported but first value matching
      # will be used before moving on to next tag.
      # This step is useful to remove any prefix or suffix from tags, only affecting the semver part when comparing tags
      tag-clean-regex:
        # Run regex.match() to extract out value if possible, otherwise keep it
        - "v([0-9].[0-9].[0-9])"

      # Selection step after filter and clean steps
      # semver order is default, choose one of them in your config
      # Ignore tag order, will parse for latest version based on semver
      tag-order: semver

      # Ignores semver, will order tags by timestamp and take latest tag
      tag-order: time
```


## Examples

Basic example. This will default to parsing semver of all tags and pick the highest semver version

```yaml
# .sgit.yml
repos:
  pykwalify:
    clone-url: git@github.com:Grokzen/pykwalify.git
    revision:
      tag: latest

# Tags list
1.0.0
0.9.0
0.8.0

# Selected tag
1.0.0
```

This example will ignore the semver and order all tags by time and pick the last one

```yaml
# .sgit.yml
repos:
  pykwalify:
    clone-url: git@github.com:Grokzen/pykwalify.git
    revision:
      tag: latest
      tag-order: time

# Tags list
0.9.0
1.0.0
0.8.0

# Selected tag
0.9.0
```

In this example we will filter out v1.0.0 as that is an unwanted tag format and we do not desire in our
parsing for the latest tag. It will default to semver comparison and select the latest version 0.9.0

```yaml
# .sgit.yml
repos:
  pykwalify:
    clone-url: git@github.com:Grokzen/pykwalify.git
    revision:
      tag: latest
      # Filter out unwanted tags based on regex match and grouping.
      # This feature works as a whitelist for what tags we want to keep
      # Multiple list values is supported
      tag-filter-regex:
        - "([0-9].[0-9].[0-9])"

# Tags list
v1.0.0
0.9.0
0.8.0

# Selected tag
0.9.0
```

In this example we want to have the latest version based on semver comparison. It will extract out the semver version
from all tags based on the regex and then do a semver comparison on the result list of items.

```yaml
# .sgit.yml
repos:
  pykwalify:
    clone-url: git@github.com:Grokzen/pykwalify.git
    revision:
      tag: latest
      # Filter out unwanted tags based on regex match and grouping
      tag-clean-regex:
        - "v([0-9].[0-9].[0-9])"

# Tags list
v1.0.0
0.9.0
v0.8.0

# Selected tag
1.0.0
```

When using both filter and clean we will filter before cleaning. In this example it will first remove all tags
that starts with `v` and any version that is not a 3 group semver version.

```yaml
# .sgit.yml
repos:
  pykwalify:
    clone-url: git@github.com:Grokzen/pykwalify.git
    revision:
      tag: latest
      # This will run before clean and 
      tag-filter-regex:
        - "([0-9].[0-9].[0-9])"
      # Filter out unwanted tags based on regex match and grouping
      tag-clean-regex:
        - "v([0-9].[0-9].[0-9])"

# Tags list
v1.0.0
0.9.0
v0.8.0
15.10

# Selected tag
0.9.0
```


## CLI

Currently you can only set the `revision.tag` key from cli. The extra options have to be added
manually to your configuration file and is not possible to set from cli.

Example how to change from a branch to a tag with one repo

```yaml
# Init new repo
sgit init

# Add a new git repo, this defaults to revision.branch=master
sgit repo add pykwalify git@github.com:Grokzen/pykwalify.git master

# To update and set a specific tag
sgit repo set pykwalify tag latest

# Update your clone to point to the tag
sgit update

# If you want the additional options with "tag-filter-regex", "tag-clean-regex" and "tag-order"
# you must add them manually to your .sgit.yml config file and then update your clone with
sgit update
```
