import argparse
import boto3
import json
import requests
import logging


class BuildTask:
    def __init__(self):
        self.extra_args = []
        self.logger = logging.Logger()
        
    def parse_args(self):
        parser = argparse.ArgumentParser()
        # single default argument
        parser.add_argument('-p', '--params', dest='params',
                            help='A JSON encoded string',
                            metavar="'{\"foo\": \"bar\"}'")
        # custom arguments
        for arg in self.extra_args:
            parser.add_argument(*arg)
        params = json.loads(self.parser.parse_args())

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

        self.params = params

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
        self.key = f'_tasks/artifacts/{self.task_id}/{self.filename}'
        self.s3_client.upload_file(
            Filename=self.filename,
            Bucket=self.bucket,
            Key=self.key,
        )

    def handler():
        raise NotImplementedError
