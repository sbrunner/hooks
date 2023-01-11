# Pre commit to update the copyright header

[pre-commit](https://pre-commit.com/) hook used to check if the copyright is up to date (using the Git history).

## Adding to your `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/sbrunner/pre-commit-copyright
    rev: <version> # Use the ref you want to point at
    hooks:
      - id: copyright
```

## Configuration

By default in the `.github/copyright.yaml` file.

Default values:

```yaml
one_date_re: ' Copyright \\(c\\) (?P<year>[0-9]{4})"))'
tow_date_re: ' Copyright \\(c\\) (?P<from>[0-9]{4})-(?P<to>[0-9]{4})")'
tow_date_format: ' Copyright (c) {from}-{to}")'
```
