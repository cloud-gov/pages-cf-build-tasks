#!/usr/bin/node
import * as ejs from 'ejs';
import { Glob } from 'glob'
import fs from 'fs';
import * as utils from './templates/utils.js';
import minimist from 'minimist';
import path from 'path';
import groupBy from 'core-js/actual/object/group-by.js';
import { marked } from 'marked';

async function renderFromTemplate(renderData, output, templateDir, templateName, buildId) {
  const templatePath = path.join(templateDir, templateName);
  const template = fs.readFileSync(templatePath, 'utf8');
  const html = await ejs.render(template, { ...renderData, utils, buildId: buildId }, { filename: `${templateDir}/${templateName}` })
  fs.writeFileSync(output, html, 'utf8');
}

function reparseHTML(str) {
  return marked.parse('\n' + str
    .replace(/<p>Phase: \b/g, '<p>##### Phase: ')
    .replace(/<[^>]*>/g, '\n')
    .replace(/(^\s +|\s + $)/gsm, '')
  )
}
function cleanAlerts (alerts, config) {
  const firstPassClean = alerts
    .map((alert) => {
      const rule = config.rules.find(rule => rule.id === alert.pluginid)
      // using our config.json, we add ignore information to alerts and instances
      const instances = alert.instances;
      if (rule) {
        if (rule.match?.length) {
          alert.instances.forEach(instance => {
            // ignore instances if uri or evidence matches rule.match
            if (
              rule.match.some(match => instance.uri.includes(match)) ||
              rule.match.some(match => instance.evidence.includes(match))
            ) {
              instance.ignore = true
              instance.ignoreSource = rule.source
            }
          })
        } else {
          // with no match property, we ignore the whole alert
          alert.ignore = true
          alert.ignoreSource = rule.source
        }

        // if all instances are ignored, the alert is ignored
        if (instances.every(instance => instance.ignore)) {
          alert.ignore = true
          alert.ignoreSource = rule.source
        }
      }

      return {
        ...alert,
        instances,
        description: reparseHTML(alert.desc),
        solution: reparseHTML(alert.solution),
        riskLabel: alert.riskdesc.split(' ', 1)[0],
        referenceURLs: !!alert.reference ? alert.reference.replace(/<[^>]*>/g, '\n').split('\n\n') : null
      }
    })

    return firstPassClean.reduce((agg, alert) => {
      // we take this second pass to create duplicate alerts for those which contain some ignored
      // and some non-ignored instances
      const test = alert.instances.some(i => i.ignore) && !alert.instances.every(i => i.ignore);
      const alertArray = test
        ? [
          { ...alert, instances: instances.filter(i => i.ignore), ignore: true },
          { ...alert, instances: instances.filter(i => !i.ignore), ignore: false },
        ]
        : [alert]
      return agg.concat(alertArray)
    }, [])
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

function prepareResults(results, config) {
  let cleanedAlerts = cleanAlerts(results.site[0].alerts, config);
  let groupedAlerts = groupAlerts(cleanedAlerts);
  return {
    site: {
      ...results.site[0],
      alerts: cleanedAlerts,
      groupedAlerts: groupedAlerts,
      issueCount: [...cleanedAlerts.filter(alert => alert.riskcode > 0 && !alert.ignore)].length
    },
    generated: results['@generated']
  };
}

const argv = minimist(process.argv.slice(2));

const {
  input: inputFile,
  output,
  templateDir,
  buildId,
  config: configFile
} = argv;

console.log(`Generating report page at ${output}`)

const contents = JSON.parse(fs.readFileSync(inputFile, "utf8"));
const config = JSON.parse(fs.readFileSync(configFile, "utf8"))

const results = prepareResults(contents, config);

await renderFromTemplate(results, output, templateDir, "report.ejs", buildId).then(console.log(`Report generation complete; open ${output} to review.`))

// write summary count to stdout to be picked up by subprocess.run
console.log(`Issue Count: ${results.site.issueCount}`)
