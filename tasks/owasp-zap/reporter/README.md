# ZAP reporter

Creates an HTML report from ZAP vulnerability scan

Given an `input` JSON file for a given `target` and a `templateDir` containing `.ejs` files, the following command creates a matching HTML report`.

```sh

node generate-report.js --input results.json --templateDir templates --target https://example.gov

```
