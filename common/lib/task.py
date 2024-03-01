import argparse
import boto3
import json
import os
import requests
import logging


class BaseBuildTask:
    def __init__(self, extra_args):
        logging.basicConfig(level=os.environ.get('LOGLEVEL', 'INFO').upper())
        self.logger = logging.getLogger(name=type(self).__name__)
        self.parser = argparse.ArgumentParser()

        # single default argument
        self.parser.add_argument('-p', '--params', dest='params',
                                 help='A JSON encoded string',
                                 metavar="'{\"foo\": \"bar\"}'")

        # custom arguments
        for arg in extra_args:
            self.parser.add_argument(*arg)

    def parse_args(self):
        args = self.parser.parse_args()

        # default argument handling
        params = json.loads(args.params)

        self.status_callback = params["STATUS_CALLBACK"]
        self.task_id = params["TASK_ID"]
        self.aws_default_region = params["AWS_DEFAULT_REGION"]
        self.aws_access_key_id = params["AWS_ACCESS_KEY_ID"]
        self.aws_secret_access_key = params["AWS_SECRET_ACCESS_KEY"]
        self.bucket = params["BUCKET"]

        self.s3_client = boto3.client(
            service_name='s3',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.aws_default_region
        )

        self.args = {}
        # custom argument handling
        for k, v in args.__dict__.items():
            if k != 'params':
                self.args[k] = v

    def status_start(self):
        """callback"""
        self.logger.info(f'Task {self.task_id} is starting')
        requests.put(self.status_callback, json={
            "status": "processing"
        })

    def status_end(self):
        """callback"""
        self.logger.info(f'Task {self.task_id} is complete')
        requests.put(self.status_callback, json={
            "artifact": self.key,
            "status": "success"
        })

    def status_error(self, err):
        """callback"""
        self.logger.error(f'Task {self.task_id} errored: {err}')
        requests.put(self.status_callback, json={
            "status": "error"
        })

    def upload_file(self):
        """upload file to S3"""

        base = os.path.basename(self.filename)
        self.key = f'_tasks/artifacts/{self.task_id}/{base}'

        self.s3_client.upload_file(
            Filename=self.filename,
            Bucket=self.bucket,
            Key=self.key,
        )

    def handler():
        raise NotImplementedError
