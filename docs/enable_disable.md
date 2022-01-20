# enable/disable repo

You can enable or disable the parsing of any repo defined in `.sgit.yml` file by adding the flag `enabled: true/false` to your repo configuration block.

If this flag is not defined or set in your configuration, it will default to `true` and a repo will be parsed by default.


## Enable a repo explicitly

```yaml
repos:
  pykwalify:
    enabled: true
    clone-url: git@github.com:Grokzen/pykwalify.git
    revision:
      branch: master
```


## Disable repo explicitly

You can disable repo with the following flag

```yaml
repos:
  pykwalify:
    enabled: false
    clone-url: git@github.com:Grokzen/pykwalify.git
    revision:
      branch: master
```


## CLI usage

To enable or disable a repo from the cli you can use the following syntax

```
sgit repo enable <repo-name>

sgit repo disable <repo-name>
```
