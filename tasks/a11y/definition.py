import json
import os
import re
import shutil
import logging

from scraper.spider import process, A11ySpider

from lib.task import BaseBuildTask
from lib.utils import run


class BuildTask(BaseBuildTask):
    def __init__(self):
        super().__init__(
            extra_args=[
                ['-t', '--target'],
                ['-b', '--buildid'],
                ['-o', '--owner'],
                ['-r', '--repository'],
                ['-c', '--config']],
        )

    def handler(self):
        """scan"""
        target = self.args['target']
        buildid = self.args['buildid']
        owner = self.args['owner']
        repository = self.args['repository']
        config = self.args['config']
        config_file = '/build-task/reporter/config.json'
        with open(config_file, 'w') as cf:
            cf.write(config)

        results_dir = '/build-task/results'
        output_dir = '/build-task/output'
        os.makedirs(results_dir, exist_ok=True)

        # crawl
        data = []  # accumulates the urls during .start()
        process.crawl(A11ySpider, target=target, data=data)
        process.start()

        # the crawler resets the log level
        self.logger.setLevel(
            logging.getLevelName(
                os.getenv('LOGLEVEL', 'debug').upper()
            )
        )
        self.logger.info(f'{len(data)} urls found')

        # scan
        for idx, url in enumerate(data):
            try:
                # capture the output to avoid printing individual page results
                self.logger.info(f'axe scan on url: {url}')
                run([
                    f'axe {url}' +
                    ' --chrome-options="no-sandbox,disable-setuid-sandbox,disable-dev-shm-usage"' +  # noqa: E501
                    ' --tags wcag2a,wcag2aa,wcag21a,wcag21aa,wcag22aa' +
                    f' --dir {results_dir}'
                ], timeout=900, shell=True, capture_output=True)
            except Exception:
                self.logger.error(f'error scanning url: {url}')
                with open(os.path.join(results_dir, str(idx)), 'w') as f:
                    json.dump([dict(url=url, error=True)], f)

        output = run([
            'node',
            'build-task/reporter/generate-report.js',
            '--inputDir',
            results_dir,
            '--outputDir',
            output_dir,
            '--target',
            target,
            '--buildId',
            buildid,
            '--config',
            config_file
        ], capture_output=True)

        # Keeping until we remove report generation
        # regex test on output for count
        summary_regex = r'Issue Count: (\d+)'
        match = re.search(summary_regex, output.stdout)
        try:
            count = int(match.groups()[0])
        except Exception:
            count = 0

        return dict(
            artifact=output_dir,
            message=None,
            count=count,
        )
