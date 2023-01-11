# Pre commit to update the copyright header

[Pre-commit](https://pre-commit.com/) hook used to check if the copyright is up to date.

### Adding to your `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/sbrunner/pre-commit-copyright
    rev: <version> # Use the ref you want to point at
    hooks:
      - id: copyright
```
