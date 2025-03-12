## 0.2.12 (2025-03-12)

### Maintenance

- update a11y reporter dependencies

## 0.2.11 (2025-01-17)

### Maintenance

- run task in virtualenv, zap in base python, per pep 668
- update reporter dependencies

## 0.2.10 (2024-11-19)

### Maintenance

- a11y count should respected ignored rules

## 0.2.9 (2024-11-14)

### Maintenance

- rotate user-agent

## 0.2.8 (2024-10-29)

### Fixed

- throw an error when no urls are found (#71)

## 0.2.7 (2024-10-10)

### Maintenance

- correct spider regex match
- drop zap run specific timeout

## 0.2.6 (2024-10-09)

### Maintenance

- lower url limit

## 0.2.5 (2024-10-08)

### Fixed

- don't use parent relative import

## 0.2.4 (2024-10-07)

### Maintenance

- add custom user-agent to a11y scans

## 0.2.3 (2024-09-27)

### Fixed

- guarantee output directory

### Maintenance

- reduce concurrent spider requests

## 0.2.2 (2024-09-26)

### Maintenance

- add logging and page delay, reorder suppressions

## 0.2.1 (2024-09-23)

### Fixed

- don't capture xml or pdf links

### Maintenance

- add ignore source for alerts with instance suppression
- Update task reporter node dependencies

## 0.2.0 (2024-09-04)

### Added

- Update release
- use supplied scan configuration

### Fixed

- use the correct variable name on second pass deduplication of ignored findings
- use base url and random sample of urls when over defined limit

### Maintenance

- new changelog
- add temp changelog
- release 0.2.0
- release 0.2.0
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
