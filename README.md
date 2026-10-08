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
      # Do uv lock, from a `*.in` file to the `*.txt` file with the hashes
      - id: uv-lock
        args:
          - --python-version=3.14
        additional_dependencies:
          - uv==<version>
      # Do Helm lock (helm should be installed)
      - id: helm-lock
      - id: npm-lock
```

## uv lock

The `uv-lock` hook compiles every `*requirements.in` file with `uv pip compile --generate-hashes`,
and writes the result in the file with the same name and the `.txt` extension. The generated file is
fully locked: every transitive dependency is pinned with its hashes, which is what a publishing job
should install.

Arguments:

- `--check`: only check that the generated file is up to date, do not write it.
- `--python-version=<version>`: the Python version used to resolve the dependencies, it should be the
  version of the interpreter that installs the generated file.
- `--extension=<extension>`: the extension of the generated file, `.txt` by default.

As with the other lock hooks, the hook modifies the file and pre-commit fails: in the continuous
integration the change is uploaded as the `Apply pre-commit fix.patch` artifact and applied by the
`patch` module of ghci, so a dependency bump of the `.in` file regenerates the `.txt` file
automatically.

## Copyright configuration

The default values used in the `.github/copyright.yaml` file.

Default values:

```yaml
one_date_re: ' Copyright \\(c\\) (?P<year>[0-9]{4})"))'
two_date_re: ' Copyright \\(c\\) (?P<from>[0-9]{4})-(?P<to>[0-9]{4})")'
one_date_format: ' Copyright (c) {year}")'
two_date_format: ' Copyright (c) {from}-{to}")'
license_file: LICENSE

one_date_re: ' Copyright \(c\) (?P<year>[0-9]{4})'
two_date_re: ' Copyright \(c\) (?P<from>[0-9]{4})-(?P<to>[0-9]{4})'
one_date_format: ' Copyright (c) {year}'
two_date_format: ' Copyright (c) {from}-{to}'
license_file: LICENSE
```
