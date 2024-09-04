## 0.2.0 (2024-09-04)

### Added

- use supplied scan configuration

### Fixed

- use the correct variable name on second pass deduplication of ignored findings
- use base url and random sample of urls when over defined limit

### Maintenance

- pull to consistent git depth
- Refactor zap and a11y tasks to upload just JSON results
- **ci**: use boot script for multiple env
- update pipeline

## 0.1.3 (2024-05-28)

### Added

- Decrypt params and args values passed to build task #4509

### Fixed

- Add self to BaseBuildTask set_encryption_key method

### Maintenance

- container hardening

## 0.1.2 (2024-04-23)

### Maintenance

- better logging, fix a11y error state

## 0.1.1 (2024-04-17)

### Added

- better vulnerability scan

### Maintenance

- better issue count for vulnerability scan, error handling

## 0.1.0 (2024-04-10)

### Added

- deploy to production space (#25)
- add issue counts
- add accessibility scan
- initial implementation of zap scan task

### Fixed

- zap report name
- don't fail zap task on warnings

### Maintenance

- use a separate cf space for build tasks
- **ci**: add tests to ci
- add tests
- add error handling
- **ci**: update staging image repo resource
- remove extra cf-image from pipelines
- **ci**: Switch to general-task and registry-image for CI jobs
- add staging pipeline (#8)
- Update resource types to use hardened images (#6)
- implement per-task build pattern (#4)