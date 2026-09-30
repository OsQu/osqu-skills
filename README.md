# Osqu skills

Requires Python 3.9 or newer.

Initialise a project's task logs and planning directory, and render skill instructions
with the same paths:

```sh
./scripts/init --project-dir /path/to/project
./scripts/install-codex
# or ./scripts/install-claude
```

Defaults live in `config/defaults.json.example`. For local configuration, copy
the example and edit `config/defaults.json`, which is ignored by Git:

```sh
cp config/defaults.json.example config/defaults.json
```

Initialization works with the example defaults when the local file is absent.
You can also supply a JSON file with overrides:

```json
{
  "tasklog_dir": "notes/tasks",
  "planning_doc_dir": "notes/plans"
}
```

```sh
./scripts/init --config /path/to/config.json --project-dir /path/to/project
```

Omitted settings retain their defaults. Local configuration overrides the example,
and `--config` overrides local configuration. `project_name` is derived from the project
directory's name. Resource paths can be relative to the project directory or
absolute. Use absolute paths for shared task log and planning directories across
repositories; each project's task log uses its project name. Existing
project files are preserved, including task logs. To render skills without
creating project resources, pass `--skills-only`.

Rendered skills live in `.generated/skills`, and both installers link to them.
Re-run init after changing source skills or configuration. These paths apply to
all projects using this installation; init with the same config when preparing
another project. Existing installations can be backed up and replaced using
the installer's `--replace-existing` flag.

Each skill may include an `init.json` with `directories` and `files` entries.
File entries specify a relative or absolute resource `path` and a skill-relative
`template`. Resource paths are rendered by template replacement and joined to
the project directory; absolute paths, `..`, and symlinks work normally.
Use `{{tasklog_dir}}`, `{{planning_doc_dir}}`, and `{{project_name}}` in resource
paths and templates. Skill instructions also support those variables. Keep
templates in the skill's `assets` folder; edit source skills, not generated files.
