import os
import re
import shutil
import subprocess

from scraper.spider import process, A11ySpider

from lib.task import BaseBuildTask


class BuildTask(BaseBuildTask):
    def __init__(self):
        super().__init__(
            extra_args=[
                ['-t', '--target'],
                ['-b', '--buildid'],
                ['-o', '--owner'],
                ['-r', '--repository']]
        )

    def handler(self):
        """scan"""
        target = self.args['target']
        buildid = self.args['buildid']
        owner = self.args['owner']
        repository = self.args['repository']

        results_dir = '/build-task/results'
        reports_dir = '/build-task/reports'
        templates_dir = '/build-task/reporter/templates'
        os.makedirs(results_dir, exist_ok=True)

        # crawl
        data = []  # accumulates the urls during .start()
        process.crawl(A11ySpider, target=target, data=data)
        process.start()

        # scan
        for url in data:
            subprocess.run([
                f'axe {url}' +
                ' --chrome-options="no-sandbox,disable-setuid-sandbox,disable-dev-shm-usage"' +
                ' --tags wcag2a,wcag2aa,wcag21a,wcag21aa,wcag22aa' +
                f' --dir {results_dir}'
            ], timeout=900, shell=True)

        # report
        output = subprocess.run([
            'node',
            'build-task/reporter/generate-report.js',
            '--inputDir',
            results_dir,
            '--outputDir',
            reports_dir,
            '--templateDir',
            templates_dir,
            '--target',
            target
        ], capture_output=True, text=True)

        # regex test on output for count
        summary_regex = r'Issue Count: (\d+)'
        match = re.search(summary_regex, output.stdout)
        try:
            count = int(match.groups()[0])
        except Exception:
            count = 0

        # bundle
        filename = f'/accessibility-scan-for-{owner}-{repository}-{buildid}'  # noqa: E501
        shutil.make_archive(filename, 'zip', reports_dir)

        return dict(
            artifact=f'{filename}.zip',
            message=None,
            count=count,
        )
