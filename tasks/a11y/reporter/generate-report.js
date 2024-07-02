#!/usr/bin/node
import { Glob } from 'glob'
import fs from 'fs';
import groupBy from 'core-js/actual/object/group-by.js';
import * as utils from './templates/utils.js';
import minimist from 'minimist';
import path from 'path';

function violationEnhancer(violation, config, url) {
  const rule = config.rules.find(rule => rule.id === violation.id)
  // if (rule.match) { ignore certain nodes }
  // else { ignore the whole violation }
  // also { if all nodes ignored, ignore the whole violation }
  let ignore = false;
  let ignoreSource = '';
  if (rule) {
    if (rule.match?.length) {
      violation.nodes.forEach(node => {
        // ignore nodes if html matches rule.match
        if (rule.match.some(match => node.html.includes(match))) {
          node.ignore = true;
          node.ignoreSource = rule.source;
        }
      })
      // ignore the violation for a url match
      if (rule.match.some(match => url.includes(match))) {
        ignore = true;
        ignoreSource = rule.source;
      }

    } else {
      // with no match property, we ignore the whole violation
      ignore = true;
      ignoreSource = rule.source;
    }

    // if all nodes are ignored, the violation is ignored
    if (violation.nodes.every(node => node.ignore)) {
      ignore = true;
      ignoreSource = rule.source;
    }
  }

  const { svg: icon, color, order } = utils.getMatchingSeverity(violation.impact);

  return {
    ...violation,
    icon,
    color,
    order,
    impact: violation.impact ?? 'other',
    description: violation.description.replace(/\bEnsures\b/g, 'Ensure'),
    total: violation.nodes.length,
    helpUrl: violation.helpUrl,
    ignore,
    ignoreSource,
    urls: [url],
  }
}

async function writeToJSON(data, filePath, outputDir) {
  fs.mkdir(outputDir, { recursive: true }, (err) => {
    console.error(err)
  })
  const outputPath = path.join(outputDir, `${filePath}.json`);
  const output = JSON.stringify(data)
  fs.writeFileSync(outputPath, output, 'utf8');
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

function enhanceViolations(allViolations, config, url) {
  return allViolations.map(v => violationEnhancer(v, config, url)).sort(sortByNodesLength)
}
function shallowViolations(allViolations, config, url) {
  return allViolations.map(v => violationEnhancer(v, config, url));
}

function prepareResults(results) {
  const enhancedViolations = enhanceViolations([...results.violations], config, results.url);
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
    shallowRulesViolated: shallowViolations([...results.violations], config, results.url)
  };
}

function keepUniqueObjectsWithTotalSorted(array) {
  return Object.values(array.reduce((acc, el) => {
    const uniqueKey = el.id;
    if (!acc[uniqueKey]) {
      acc[uniqueKey] = el;
    } else {
      acc[uniqueKey].total += el.total;
      acc[uniqueKey].urls.push(...el.urls);
    }
    return acc;
  }, {})).sort((a, b) => a.order - b.order || b.total - a.total || a.id.localeCompare(b.id));
}

const argv = minimist(process.argv.slice(2));

let inputPath = argv.inputDir;
let outputPath = argv.outputDir;
let buildId = argv.buildId;
let configFile = argv.config;

const config = JSON.parse(fs.readFileSync(configFile, "utf8"))

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
  let contents = [];
  try {
    contents = JSON.parse(fs.readFileSync(file, "utf8"));
  } catch(error) {
    console.error("Could not parse results file", file, error);
    contents = [{
      error: true,
      url: null
    }]
  }

  if (contents[0]?.error) {
    accumulator.reportPages.push({
      failed: true,
      path: null,
      absoluteURL: contents[0].url?.toString() || null,
      relativeURL: contents[0].url?.split(accumulator.baseurl)[1].toString() || null,
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

    await writeToJSON(thisPage.renderData, fileName, outputPath).then(() => {

      accumulator.reportPages.push({
        path: `${fileName}`,
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
    await writeToJSON(accumulator, '/index', outputPath).then(console.log(`Report generation for build id: ${buildId} complete; open ${outputPath}/index.html to review.`))

    // write summary count to stdout to be picked up by subprocess.run
    console.log(`Issue Count: ${accumulator.violatedRules.length}`)

  }
}
