#!/usr/bin/node
import * as ejs from 'ejs';
import { Glob } from 'glob'
import fs from 'fs/promises';
import groupBy from 'core-js/actual/object/group-by.js';
import * as utils from './templates/utils.js';
import minimist from 'minimist';
import path from 'path';

async function renderFromTemplate(renderData, accumulator, filePath, outputDir, templateDir, templateName, buildId) {

  const templatePath = path.join(templateDir, templateName);
  await fs.mkdir(outputDir, { recursive: true })
  const outputPath = path.join(outputDir, `${filePath}.html`);
  const template = await fs.readFile(templatePath, 'utf8');
  const html = await ejs.render(template, { ...renderData, accumulator, utils, buildId: buildId }, { filename: `${templateDir}/${templateName}` })
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
function shallowViolations(allViolations) {
  return allViolations.map((check) => ({
    id: check.id,
    color: utils.getMatchingSeverity(check.impact).color,
    order: utils.getMatchingSeverity(check.impact).order,
    impact: check.impact ?? 'other',
    description: check.description.replace(/\bEnsures\b/g, 'Ensure'),
    total: check.nodes.length,
    helpUrl: check.helpUrl,
  }))
}

function prepareResults(results) {
  const enhancedViolations = enhanceViolations([...results.violations]);
  let groupedViolations = groupViolations(enhancedViolations);
  return {
    renderData: {
      url: results.url,
      timestamp: results.timestamp,
      passes: results.passes.map((check) => ({
        ...check,
      })).sort(sortByNodesLength),
      groupedViolations: groupedViolations,
      violationsCount: results.violations.length,
    },
    shallowRulesViolated: shallowViolations([...results.violations])
  };
}

function keepUniqueObjectsWithTotalSorted(array) {
  return Object.values(array.reduce((acc, el) => {
    const uniqueKey = el.id;
    if (!acc[uniqueKey]) {
      acc[uniqueKey] = el;
    } else {
      acc[uniqueKey].total += el.total;
    }
    return acc;
  }, {})).sort((a, b) => a.order - b.order || b.total - a.total || a.id.localeCompare(b.id));
}

const argv = minimist(process.argv.slice(2));

let inputPath = argv.inputDir;
let outputPath = argv.outputDir;
let templatePath = argv.templateDir;
let buildId = argv.buildId;

const g = new Glob(`${inputPath}/*`, {});
const totalLength = g.walkSync().length;

let accumulator = {
  baseurl: argv.target || "",
  totalPageCount: totalLength,
  totalViolationsCount: 0,
  violatedRules: [],
  currentPage: 0,
  reportPages: [],
}


console.log(`Generating report pages at ${outputPath}/`)

for await (const file of g) {
  let contents = JSON.parse(await fs.readFile(file, "utf8"));
  if (contents[0]?.error) {
    accumulator.reportPages.push({
      failed: true,
      path: null,
      absoluteURL: contents[0].url,
      relativeURL: contents[0].url.split(accumulator.baseurl)[1],
      indexPills: [],
      moreCount: null
    });

    accumulator.currentPage++;
    console.log(`No valid JSON results found for '${contents[0].url}'; report will not be generated.`)

  } else {
    let thisPage = prepareResults(contents[0]);
    const fileName = path.parse(file).name

    let groupedViolationsCounts = [];

    Object.keys(thisPage.renderData.groupedViolations).forEach((name) => {
      groupedViolationsCounts.push({ name: name, count: thisPage.renderData.groupedViolations[name].length })
    });
    let indexPills = groupedViolationsCounts.slice(0, 2);

    let moreCount = groupedViolationsCounts.slice(2).reduce((total, pill) => total + pill.count,
      0,)

    await renderFromTemplate(thisPage.renderData, accumulator, fileName, outputPath, templatePath, "reportPage.ejs", buildId).then(() => {



      accumulator.reportPages.push({
        path: `${fileName}.html`,
        absoluteURL: thisPage.renderData.url,
        relativeURL: thisPage.renderData.url.split(accumulator.baseurl)[1],
        timestamp: thisPage.renderData.timestamp,
        violationsCount: thisPage.renderData.violationsCount,
        groupedViolationsCounts: groupedViolationsCounts,
        indexPills: indexPills,
        moreCount: moreCount
      });

      accumulator.currentPage++;
      accumulator.totalViolationsCount += thisPage.renderData.violationsCount;

      thisPage.shallowRulesViolated.forEach((rule) => {
        accumulator.violatedRules.push(rule)
      });

      // note that url is a sort of user-provided value; it's using whatever the scanned URL was, not the json results filename.
      console.log(`Generating report for ${thisPage.renderData.violationsCount} accessibility violations found at '${thisPage.renderData.url}'`)

    })
  }

  if (accumulator.currentPage == totalLength) {
    accumulator.violatedRules = keepUniqueObjectsWithTotalSorted(accumulator.violatedRules);
    // sort summary by most results per page
    accumulator.reportPages = accumulator.reportPages.sort((a, b) => b.violationsCount - a.violationsCount)
    console.log(`Generating report index for ${buildId}: ${accumulator.violatedRules.length} accessibility violations found in ${accumulator.totalViolationsCount} locations across ${totalLength} URLs.`)
    await renderFromTemplate(null, accumulator, '/index', outputPath, templatePath, "reportIndex.ejs", buildId).then(console.log(`Report generation for build id: ${buildId} complete; open ${outputPath}/index.html to review.`))

    // write summary count to stdout to be picked up by subprocess.run
    console.log(`Issue Count: ${accumulator.violatedRules.length}`)

  }
}

