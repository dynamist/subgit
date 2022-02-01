# Revision: tag

If you want to use the more specialized and advanced option for parsing and selecting a specific tag from a git repo then you should use the tag revision option.

This is the following syntax and extra options. More detailed examples is further down in this document.

```yaml
repos:
  pykwalify:
    clone-url: git@github.com:Grokzen/pykwalify.git
    revision:
      tag:
        # One regex string or a list of regex strings is supported here
        # Filter is the first step and the purpose is two fold where one
        # is that you want to filter out a specific set of tags based on a pattern matching.
        # The second feature is that if you make a regex match group you can extract out
        # any value from within the string in case you need to clean away unwanted data.
        # A common case is that semver tags is named v1.0.0 where we only want 1.0.0 to perform
        # a semver comparison against. For a good example where this is very usefull please check
        # the azure-python-sdk git mono repo.
        # If filter key is not present or is an empty string or empty list all values
        # will be preserved in the output.
        filter: "my-sdk-[0-9].[0-9].[0-9]"

        # Or in list form with multiple values. With multiple values, any value that wants to be preserved must match
        # at least one of them, but not all of them. This is considred a whitelist & extract operation.
        filter:
          - "([0-9].[0-9].[0-9])"
          - "v([0-9].[0-9].[0-9])"

        # Second step is to order the output from the filter step. In most cases the default semver
        # ordering is what you want by default. How to think about it is that if you order something
        # you will order the "top" or latest item to the right and the lower items to the
        # left or begining of a list.
        # If you order ["1.0.0", "1.1.0", "0.9.0"] it will semver sort to ["0.9.0", "1.0.0", "1.1.0"]
        # This means that if you later on in the selection stage choose "last" or "first" special keywords,
        # you will get the first or last item in the output list from this step.
        # If you order it by time, for tags it will look only at the timestamp of when the tag
        # was created and ignores the semver version or the content of the tag string.
        # Alphabetical ordering will simply sort all items based on their string content only.
        # Order defaults to semver
        order: "semver|time|alphabetical"

        # Last step is to select one item out from the output from the order step.
        # Two special keywords exists, "first" and "last". They will pick the first or last item from the list
        # of items from the order step. In the most common case for simple git repos, you want to select the last
        # tag from any tag in the git repo as they only make tags on their master branch and only sequential version increases.
        # This will not work in cases like big shared mono repos with tags for different components where if you do not
        # filter out what you want properly, you will get the latest tag for a random component which might be wrong for
        # your needs
        # By default the selection method will be semver comparison defined by PEP440. This mean you can do selections
        # with >, <, >=, <=, == etc to select out the version you want. Note here that if your selection matches multiple
        # versions, it will take the last item in the list by default.
        select: ">=1.0.0"

        # Select supports child arguments in the following format. This makes it possible to change some of the parameters
        # in the selection method to be either SEMVER or EXACT. EXACT means that you make a plain string comparison
        # between what you specify in the "value" field and what you have in your input list. This is equal to
        # "if str_a == str_b" and the first match will be the returned item. If you have no match it will fail out
        # as the selection you want do not exists. EXACT option should be chosen if you care less about semver and want
        # to ignore filters and order and do more plain string selection.
        select:
          value: "abc-1.0.0"
          method: "exact"
```


## Examples

Basic example. This example will not filter out any items, it will order them by semver and the selection want the latest tag based on semver comparison. This will result in `1.0.0` as the output when doing `sgit update`

```yaml
# .sgit.yml
repos:
  pykwalify:
    clone-url: git@github.com:Grokzen/pykwalify.git
    revision:
      tag:
        select: last

# Tags list
1.0.0
0.9.0
0.8.0

# Selected tag
1.0.0
```

This example will ignore the semver and order all tags by time and pick the last one. Note this example is not super realistic as the ordering based on the semver looks wrong. But in this case we are working with git-flow model and we have support branches where old minor version tags can be created after new:er releases have been done. Time ordering is more suited for single release branch repos and not git-flow model git repos.

```yaml
# .sgit.yml
repos:
  pykwalify:
    clone-url: git@github.com:Grokzen/pykwalify.git
    revision:
      tag:
        order: time
        select: last

# Tags list
1.0.0 (created 2021-01-01)
0.8.1 (created 2022-12-01)
0.8.0 (created 2020-01-01)

# Selected tag
0.8.1
```

In this example we will filter out v1.0.0 as that is an unwanted tag format and we do not desire in our
parsing for the latest tag. It will default to semver comparison and select the latest version 0.9.0.

```yaml
# .sgit.yml
repos:
  pykwalify:
    clone-url: git@github.com:Grokzen/pykwalify.git
    revision:
      tag:
        # Filter out unwanted tags based on regex match and grouping.
        # This feature works as a whitelist for what tags we want to keep
        # Multiple list values is supported
        filter: "([0-9].[0-9].[0-9])"
        select: "last"

# Tags list
v1.0.0
0.9.0
0.8.0

# Selected tag
0.9.0
```

In this example we want to have the latest semver version. It will extract out the semver version from all tags based on the regex and then do a semver comparison on the result list of items.

```yaml
# .sgit.yml
repos:
  pykwalify:
    clone-url: git@github.com:Grokzen/pykwalify.git
    revision:
      tag:
        # Filter out the "v" from some tags, and keep the regular semver tags
        filter:
          - "[0-9].[0-9].[0-9]"
          - "v([0-9].[0-9].[0-9])"
        select: "last"

# Tags list
v1.0.0
0.9.0
v0.8.0

# Selected tag
1.0.0
```

In this example we can limit the version we want to select to a older tag based on semver comparison.

```yaml
# .sgit.yml
repos:
  pykwalify:
    clone-url: git@github.com:Grokzen/pykwalify.git
    revision:
      tag:
        select: "<1.0.0"

# Tags list
1.0.0
0.9.0
0.8.0

# Selected tag
0.9.0
```
