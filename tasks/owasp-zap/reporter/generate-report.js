#!/usr/bin/node
import * as ejs from 'ejs';
import { Glob } from 'glob'
import fs from 'fs/promises';
import * as utils from './templates/utils.js';
import minimist from 'minimist';
import path from 'path';
import groupBy from 'core-js/actual/object/group-by.js';
import { marked } from 'marked';

async function renderFromTemplate(renderData, output, templateDir, templateName, buildId) {
  const templatePath = path.join(templateDir, templateName);
  const template = await fs.readFile(templatePath, 'utf8');
  const html = await ejs.render(template, { ...renderData, utils, buildId: buildId }, { filename: `${templateDir}/${templateName}` })
  fs.writeFile(output, html, 'utf8');
}

function reparseHTML(str) {
  return marked.parse('\n' + str
    .replace(/<p>Phase: \b/g, '<p>##### Phase: ')
    .replace(/<[^>]*>/g, '\n')
    .replace(/(^\s +|\s + $)/gsm, '')
  )
}
function cleanAlerts (alerts) {
  return alerts.map((alert) => {
    return {
      ...alert,
      description: reparseHTML(alert.desc),
      solution: reparseHTML(alert.solution),
      riskLabel: alert.riskdesc.split(' ', 1)[0],
      referenceURLs: !!alert.reference ? alert.reference.replace(/<[^>]*>/g, '\n').split('\n\n') : null
    }
  })
}

function groupAlerts(alerts) {
  let groups = {};
  let matchingAlerts = groupBy(alerts, (alert) => alert.riskcode)
  utils.severity.forEach(({ riskCode }) => {
    if (!!matchingAlerts[riskCode]) {
      groups[riskCode] = matchingAlerts[riskCode] || []
    };
  })
  return groups;
}

function prepareResults(results) {
  let cleanedAlerts = cleanAlerts(results.site[0].alerts);
  return {
    site: {
      ...results.site[0],
      alerts: cleanedAlerts,
      groupedAlerts: groupAlerts(cleanedAlerts)
    },
    generated: results['@generated']
  };
}

const argv = minimist(process.argv.slice(2));

let inputFile = argv.input;
let output = argv.output;
let templateDir = argv.templateDir;
let buildId = argv.buildId;

console.log(`Generating report page at ${output}`)

let contents = JSON.parse(await fs.readFile(inputFile, "utf8"));

let results = prepareResults(contents);

await renderFromTemplate(results, output, templateDir, "report.ejs", buildId).then(console.log(`Report generation complete; open ${output} to review.`))

