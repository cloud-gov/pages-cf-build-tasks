ARG BASE_IMAGE
# use custom build image
FROM $BASE_IMAGE

# cf task will always run here (and reset other images)
WORKDIR /
USER root

# set other env variables
RUN mkdir build-task
ARG TASK_FOLDER
ADD $TASK_FOLDER build-task/
RUN export $(xargs <build-task/.env)

# Some base images have an externally managed python environment
# for the dependencies required to run the script. if we try to pip install our own
# dependencies here, we will see "error: externally-managed-environment"
# https://peps.python.org/pep-0668/
# so we (might) need to install virtualenv:
#   On Debian/Ubuntu systems, you need to install the python3-venv
#   package using the following command.
# Images this is needed for currently: zap-stable
RUN apt update && apt install python3.11-venv -y

# add necessary python dependencies
# TODO: how do we know we have python?
# TODO: could make this a requirement of the build script/image
RUN python3 -m venv task
ENV VIRTUAL_ENV /task
ENV PATH /task/bin:$PATH
RUN pip3 install --no-cache-dir --upgrade boto3 requests argparse cryptography

# run the custom build script (python dependencies here will be in the virtual env)
RUN build-task/build.sh

# copy common files, restructure
ADD common/ build-task/
RUN mv build-task/definition.py build-task/lib/definition.py

# this is always our entrypoint
ENTRYPOINT ["python", "build-task/main.py"]
