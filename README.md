# pages-cf-build-tasks

**THIS IS A TEMP BRANCH TO RESET DEV**

This repository is a monorepo for all cloud.gov Pages build tasks which run as [Cloud Foundry Tasks](https://docs.cloudfoundry.org/devguide/using-tasks.html).

## Outline

Each task has its own subfolder in `tasks/`. These subfolders contain all the task-specific code needed to both create (via Docker and Cloud Foundry) and run the task.

Shared code used across tasks is located in `lib/`.

## Container Hardening + ECR Storage

hardening: TBD

All container images are stored in the `pages-cf-build-tasks` repository on ECR. They are tagged with the task folder name and environment name: `((build-task))-((deploy-env))`

## Patterns

### New Build Task Migrations

New build tasks are registered in the [pages-core](https://github.com/cloud-gov/pages-core/) application by creating a new `BuildTaskType` instance via migration. They should follow this standard:

```js
await db.insert('build_task_type',
  ['name', 'description', 'metadata', 'createdAt', 'updatedAt', 'runner', 'startsWhen', 'url'],
  [
    taskTypeName,
    taskTypeDescription,
    {
    "appName": appName,
    "template": {
        "command": `python build-task/main.py ${additionalFlags}`,
        "disk_in_mb": diskInMb
    }
    },
    new Date(),
    new Date(),
    'cf_task',
    startsWhen,
    url
],
callback
);
```

The operator should supply the following values:

- `taskTypeName`: A human-readable task name. Example: "OWASP ZAP Vulnerability Scan"
- `taskTypeDescription`: A human-readable task description. Example: "This scan identifies potential website security issues like unintended exposure of sensitive data, SQL injection opportunities, cross-site scripting (XSS) flaws, and the use of components with known vulnerabilities."
- `appName`: A [`kebab-case`](https://developer.mozilla.org/en-US/docs/Glossary/Kebab_case) application name for the matching Cloud Foundary app this will be deployed as. It should include a template variable `env` for matching the various deployed environments (`dev`, `staging`, `production`). Example: `pages-owasp-zap-task-${env}`. This will correspond to the folder in this repo that hosts the code.
- `additionalFlags`: see [Docker Command](#docker-command)
- `diskInMb`: An integer value of the disk-space necessary (in megabytes) for running the docker image of the task.
- `startsWhen`: One of `build` or `complete`. Tasks marked `build` will run at the start of an associated Pages build. Tasks marked `complete` will run after the build completes.
- `url`: A link to additional documentation about the task.

### Docker Command

The [command](https://docs.docker.com/engine/reference/run/) sent to a build task will always be of the following form:

```sh
python build-task/main.py <operator-defined-flags> <default-parameters>
```

> [!NOTE]
> This section is a bit technical, requires fairly detailed knowledge of `pages-core`, and possibly needs further clarification. Please flag any questions or improvements as issues/PRs

- `operator-defined-flags`: These flags are used for information that the `pages-core` application should pass to the build task. They are defined in the migration (as shown above) and take the form `-x {{templated information}} -y {{more info}} -z {{etc}}`. For templating, they have access to a single model/variable `task` within `pages-core`: this is the [`BuildTask` model](https://github.com/cloud-gov/pages-core/blob/main/api/models/build-task.js) and provides access to all associated properties, as well as those on linked models (`Build`, `BuildType`, `Site`). For example, if the task requires a site's url to scan, this could be passed as a "target" flag like so: `--target {{task.Build.url}}`. Within the task code, the operator must register these added flags (method: TBD) to access it within their code.

- `default-parameters`: These parameters are always sent by the `pages-core` application and are necessary for use in the common steps like updating the build task status and uploading artifacts to S3. These parameters include the following values: `STATUS_CALLBACK`, `TASK_ID`, `AWS_DEFAULT_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `BUCKET` and are available inside the task script as `params[parameter_name]` (example `params['TASK_ID']`)

### Writing New Task Code

Adding the code for a new task is done in this repository. Each task
needs a folder within `tasks` which should be named corresponding to the `appName` defined above (example: the folder `example` becomes `pages-example-task-dev`). There are two files required to be inside this folder and a third optional file:
- `definition.py`: This is the main site of task-specific code. It needs to export one class, a subclass of [`BaseBuildTask`](lib/task.py). The custom class has two requirements:
  1. It must implement a `handler` function which returns a dictionary with three keys:
  ```python
  {
    'artifact': '/absolute/path/to/file'
    'message': 'task message',
    'count': 5 # count of "issues" raised by the scan
  }
  ```
  2. It has extra parsers defined for any `operator-defined-flags`. An example is shown at [`tasks/example/definition.py`](tasks/example/definition.py)
- `.env`: Environment variables which are added as [Build arguments](https://docs.docker.com/build/guide/build-args/) to the final docker image. The only required value is `BASE_IMAGE`.
- `build.sh`: (optional) This script is run to configure task-specific dependecies needed in the final docker image.

### Docker Image Building in CI

All tasks use the same `Dockerfile` with different build arguments supplied. Each task is built via the concourse task [`oci-build-task`](https://github.com/concourse/oci-build-task). The `.env` file referenced above is supplied as `BUILD_ARGS_FILE` so that `BASE_IMAGE` is available at build time. `TASK_FOLDER` is interpolated by the concourse `across` step and supplied as `BUILD_ARG_TASK_FOLDER`. All base images are required to have python available.
