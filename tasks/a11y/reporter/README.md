# axe-reporter-html

[Forked from `axe-reporter-html`](https://github.com/Widen/axe-reporter-html/)

Creates an HTML report from Axe results listing violations, passes, incomplete
and incompatible results.

Given an `inputDir` containing JSON files from [@axe-core/cli](https://www.npmjs.com/package/@axe-core/cli) for a given `target`, the following command creates matching HTML reports in an `outputDir`.

```sh

node generate-report.js --inputDir results --outputDir reports --target https://example.gov

```
