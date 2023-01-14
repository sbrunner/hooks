# Pre commit hooks

[pre-commit](https://pre-commit.com/) hook used to...

Check if the copyright is up to date (using the Git history).

## Adding to your `.pre-commit-config.yaml`

Check that the copyright is up to date:

```yaml
repos:
  - repo: https://github.com/sbrunner/pre-commit-hooks
    rev: <version> # Use the ref you want to point at
    hooks:
      - id: copyright
```

Check that the copyright is present and up to date:

```yaml
repos:
  - repo: https://github.com/sbrunner/pre-commit-hooks
    rev: <version> # Use the ref you want to point at
    hooks:
      - id: copyright-required
```

Required timeout in GitHub workflow files:

```yaml
repos:
  - repo: https://github.com/sbrunner/pre-commit-hooks
    rev: <version>
    hooks:
      - id: workflows-require-timeout
```

Check Poetry config:

```yaml
repos:
  - repo: https://github.com/sbrunner/pre-commit-hooks
    rev: <version>
    hooks:
      - id: poetry-check
        additional_dependencies:
          - poetry==<version>
```

Do Poetry lock:

```yaml
repos:
  - repo: https://github.com/sbrunner/pre-commit-hooks
    rev: <version>
    hooks:
      - id: poetry-lock
        additional_dependencies:
          - poetry==<version>
```

Do Pipfile lock:

```yaml
repos:
  - repo: https://github.com/sbrunner/pre-commit-hooks
    rev: <version>
    hooks:
      - id: pipenv-lock
        additional_dependencies:
          - pipenv==<version>
```

Do Helm lock:

```yaml
repos:
  - repo: https://github.com/sbrunner/pre-commit-hooks
    rev: <version>
    hooks:
      - id: helm-lock
```

## Copyright configuration

The default values used in the `.github/copyright.yaml` file.

Default values:

```yaml
one_date_re: ' Copyright \\(c\\) (?P<year>[0-9]{4})"))'
tow_date_re: ' Copyright \\(c\\) (?P<from>[0-9]{4})-(?P<to>[0-9]{4})")'
tow_date_format: ' Copyright (c) {from}-{to}")'
```
