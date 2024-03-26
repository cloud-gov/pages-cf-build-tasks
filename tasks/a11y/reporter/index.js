#!/usr/bin/node
import * as ejs from 'ejs';
import { Glob } from 'glob'
import fs from 'fs/promises';
import groupBy from 'core-js/actual/object/group-by.js';
import * as utils from './templates/utils.js';

async function renderFromTemplate(renderData, accumulator, filePath, outputPath, templatePath, templateName) {

  const templateURL = new URL(`./${templatePath}/${templateName}`, import.meta.url);
  const outputURL = new URL(`./${outputPath}${filePath}.html`, import.meta.url);
  const template = await fs.readFile(templateURL, 'utf8');
  const html = await ejs.render(template, { ...renderData, accumulator, utils }, { filename: `${templatePath}/${templateName}` })
  fs.writeFile(outputURL, html, 'utf8');
}

function groupViolations(allViolations) {
  let groups = {};
  let matchingViolations = groupBy(allViolations, (violation) => violation.impact)
  utils.allSeverities.forEach(key => {
    groups[key] = matchingViolations[key] || [];
  })
  return groups;
}

function sortByNodesLength(a, b) { return b.nodes.length - a.nodes.length }

function enhanceViolations(allViolations) {
  return allViolations.map((check) => ({
    ...check,
    icon: utils.getMatchingSeverity(check.impact).svg,
    color: utils.getMatchingSeverity(check.impact).color,
    impact: check.impact ?? 'n/a',
    description: check.description.replace(/\bEnsures\b/g, 'Ensure'),
  })).sort(sortByNodesLength)
}

function prepareResults(results) {
  return {
    ...results,
    // sort passes by #
    passes: results.passes.map((check) => ({
      ...check,
    })).sort(sortByNodesLength),
    // group violations for more organized display
    groupedViolations: groupViolations(enhanceViolations(results.violations)),
  };
}

const g = new Glob('results/*', {});
const totalLength = g.walkSync().length;

let accumulator = {
  baseurl: "https://federalist-not-a-real-hash-dd6b-e58e04b1-44ce-efde9f29dd6b.sites.pages.cloud.gov/preview/cloud-gov/repo-name/branch-name", // can we get this from pages?
  repo_and_branch: "org-name/repo-name/branch-name",
  totalPageCount: totalLength,
  totalViolationsCount: 0,
  currentPage: 0,
  reportPages: [],
}
let outputPath = '_site'; // ok to get from command line?
let templatePath = 'templates'; // ok to get from command line?

console.log(`Generating report pages at ${outputPath}/`)

for await (const file of g) {
  let contents = JSON.parse(await fs.readFile(file, "utf8"));
  let thisPage = prepareResults(contents[0]);
  const fileName = file.substring(file.lastIndexOf('/'), file.lastIndexOf('.')) || file;

  await renderFromTemplate(thisPage, accumulator, fileName, outputPath, templatePath, "reportPage.ejs").then(() => {
    accumulator.reportPages.push({
      path: `${fileName}.html`,
      url: thisPage.url,
      timestamp: thisPage.timestamp,
      violationsCount: thisPage.violations.length,
      groupedViolationsCounts: Object.fromEntries(
        utils.allSeverities.map(severity => [severity, thisPage.groupedViolations[severity].length]))
    });

    accumulator.currentPage++;
    accumulator.totalViolationsCount += thisPage.violations.length;
    // note that url is a sort of user-provided value; it's using whatever the scanned URL was, not the json results filename.
    console.log(`Generating report for ${thisPage.violations.length} accessibility violations found at '${thisPage.url}'`)

  })
  if (accumulator.currentPage == totalLength) {
    // sort summary by most results per page
    accumulator.reportPages = accumulator.reportPages.sort((a, b) => b.violationsCount - a.violationsCount)
    console.log(`Generating report index for ${accumulator.totalViolationsCount} accessibility violations found across ${totalLength} URLs.`)
    await renderFromTemplate(null, accumulator, '/index', outputPath, templatePath, "reportIndex.ejs").then(console.log(`Report generation complete; open ${outputPath}/index.html to review.`))
  }
}

