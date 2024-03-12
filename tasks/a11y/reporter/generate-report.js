#!/usr/bin/node
import * as ejs from 'ejs';
import { Glob } from 'glob'
import fs from 'fs/promises';
import groupBy from 'core-js/actual/object/group-by.js';
import * as utils from './templates/utils.js';
import minimist from 'minimist';
import path from 'path';

async function renderFromTemplate(renderData, accumulator, filePath, outputDir, templateDir, templateName) {

  const templatePath = path.join(templateDir, templateName);
  await fs.mkdir(outputDir, { recursive: true })
  const outputPath = path.join(outputDir, `${filePath}.html`);
  const template = await fs.readFile(templatePath, 'utf8');
  const html = await ejs.render(template, { ...renderData, accumulator, utils }, { filename: `${templateDir}/${templateName}` })
  fs.writeFile(outputPath, html, 'utf8');
}

function groupViolations(allViolations) {
  let groups = {};
  let matchingViolations = groupBy(allViolations, (violation) => violation.impact)
  utils.severity.forEach(({ name }) => {
    if (!!matchingViolations[name]) {
      return groups[name] = matchingViolations[name] || [];
    }
  })
  return groups;
}

function sortByNodesLength(a, b) { return b.nodes.length - a.nodes.length }

function enhanceViolations(allViolations) {
  return allViolations.map((check) => ({
    ...check,
    icon: utils.getMatchingSeverity(check.impact).svg,
    color: utils.getMatchingSeverity(check.impact).color,
    impact: check.impact ?? 'other',
    description: check.description.replace(/\bEnsures\b/g, 'Ensure'),
  })).sort(sortByNodesLength)
}

function prepareResults(results) {
  let groupedViolations = groupViolations(enhanceViolations([ ...results.violations]));
  return {
    ...results,
    // sort passes by #
    passes: results.passes.map((check) => ({
      ...check,
    })).sort(sortByNodesLength),
    // group violations for more organized display
    groupedViolations: groupedViolations,
  };
}

const argv = minimist(process.argv.slice(2));

let inputPath = argv.inputDir;
let outputPath = argv.outputDir;
let templatePath = argv.templateDir;

const g = new Glob(`${inputPath}/*`, {});
const totalLength = g.walkSync().length;

let accumulator = {
  baseurl: argv.target || "",
  totalPageCount: totalLength,
  totalViolationsCount: 0,
  currentPage: 0,
  reportPages: [],
}


console.log(`Generating report pages at ${outputPath}/`)

for await (const file of g) {
  let contents = JSON.parse(await fs.readFile(file, "utf8"));
  let thisPage = prepareResults(contents[0]);
  const fileName = path.parse(file).name
  
  let groupedViolationsCounts = [];

  Object.keys(thisPage.groupedViolations).forEach(( name ) => {
      groupedViolationsCounts.push({ name: name, count: thisPage.groupedViolations[name].length })
    });
  let indexPills = groupedViolationsCounts.slice(0, 2);

  let moreCount = groupedViolationsCounts.slice(2).reduce((total, pill) => total + pill.count,
    0,)

  await renderFromTemplate(thisPage, accumulator, fileName, outputPath, templatePath, "reportPage.ejs").then(() => {



    accumulator.reportPages.push({
      path: `${fileName}.html`,
      absoluteURL: thisPage.url,
      relativeURL: thisPage.url.split(accumulator.baseurl)[1],
      timestamp: thisPage.timestamp,
      violationsCount: thisPage.violations.length,
      groupedViolationsCounts: groupedViolationsCounts,
      indexPills: indexPills,
      moreCount: moreCount
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

