# Pre commit hooks

[pre-commit](https://pre-commit.com/) hook used to...

Check if the copyright is up to date (using the Git history).

## Adding to your `.pre-commit-config.yaml`

```yaml
ci:
  skip:
    # Skip the copyright check on pre-commit.ci because we don't have the Git history
    - copyright
    - copyright-required
    # Poetry didn't works with Python 3.11
    - poetry-lock
    - poetry-check

repos:
  - repo: https://github.com/sbrunner/hooks
    rev: <version> # Use the ref you want to point at
    hooks:
      # Check that the copyright is up to date
      - id: copyright
      # Check that the copyright is present and up to date
      - id: copyright-required
      # Require a timeout in GitHub workflow files
      - id: workflows-require-timeout
      # Check Poetry config
      - id: poetry-check
        additional_dependencies:
          - poetry==<version>
      # Do Poetry lock
      - id: poetry-lock
        additional_dependencies:
          - poetry==<version>
      # Do Pipfile lock
      - id: pipenv-lock
        additional_dependencies:
          - pipenv==<version>
      # Do Helm lock (helm should be installed)
      - id: helm-lock
      - id: npm-lock
```

## Copyright configuration

The default values used in the `.github/copyright.yaml` file.

Default values:

```yaml
one_date_re: ' Copyright \\(c\\) (?P<year>[0-9]{4})"))'
two_date_re: ' Copyright \\(c\\) (?P<from>[0-9]{4})-(?P<to>[0-9]{4})")'
one_date_format: ' Copyright (c) {year}")'
two_date_format: ' Copyright (c) {from}-{to}")'
license_file: LICENSE
```
