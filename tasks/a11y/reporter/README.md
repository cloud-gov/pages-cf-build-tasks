# axe-reporter-html

[Forked from `axe-reporter-html`](https://github.com/Widen/axe-reporter-html/)

Creates an HTML report from Axe results listing violations, passes, incomplete
and incompatible results.

Given an `inputDir` containing JSON files from [@axe-core/cli](https://www.npmjs.com/package/@axe-core/cli) for a given `target`, the following command creates matching JSON reports in an `outputDir`.

```sh

node generate-report.js --inputDir results --outputDir reports --target https://example.gov

```

## Output

The scan results are stored as JSON objects in the site's S3 bucket under the task id's key.
The file structure consist of an `index.json` that is used to summarize all of the identified violated rules, list the violations, and provide a path to the results page.

```json
// index
{
  // The site's base url
  "baseurl": "https://example.gov",
  // Total number of site pages with rule violations
  "totalPageCount": 8,
  // Total Violations
  "totalViolationsCount": 11,
  // List of the rules that are violated across the site
  "violatedRules": [
    {
      // Violation ID
      "id": "rules-x-violated",
      // Violation impact level
      "impact": "serious",
      // Description of violation
      "description": "This rule x expects this to be y.",
      // Help text to fix the violation
      "help": "Update x to be more like y",
      // List of nodes violating the rule in the site
      "nodes": [{}],
      // Error color
      "color": "error-dark",
      // Error order
      "order": 1,
      // Total number of occurences the rule was violated
      "total": 8,
      // If the violation rule should be ignored
      "ignore": false,
      // The source used to ignore the rule
      "ignoreSource": ""
    }
  ],
  "currentPage": 8,
  // List of all of the report pages with information summarrized the page's violations
  "reportPages": [
    {
      // The ouput scan result page
      // /sites/:site_id/builds/:build_id/scans/:task_id/axe-results-12345
      "path": "axe-results-12345",
      // The url of the site's page with the reported violations
      "absoluteURL": "https://test.example.gov/page/",
      // Timestamp of the test
      "timestamp": "YYYY-MM-DDTHH:ss:SSS",
      // Total violations found on site's page
      "violationsCount": 2,
      // Summary of the violation types an count
      "groupedViolationsCounts": [{ "name": "serious", "count": 2 }],
      // Summary of the violation types an count
      "indexPills": [{ "name": "serious", "count": 2 }],
      "moreCount": 0
    }
  ]
}

```

The additional results generated are identifying each page of the site that has at least one violation identitfied.

```json
// axe-result-12345
{
    // The url of the site's page with the reported violations
    "url": "https://test.example.gov/page/",
    // Timestamp of the test
    "timestamp": "YYYY-MM-DDTHH:ss:SSS",
    // An array of rules tested that passed on the page
    "passes": [],
    // An object grouping violations based their violation type
    // Each violation type is an array of the violations identified
    "groupedViolations": {
      "critical": [...],
      "serious": [...],
      ...
    },
    // Total number of violations found on pages
    "violationsCount": 2
}
```
