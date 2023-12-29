ARG BASE_IMAGE
# use custom build image
FROM $BASE_IMAGE
 
# cf task will always run here (and reset other images)
WORKDIR /
USER root

# add necessary python dependencies
# TODO: how do we know we have python?
# TODO: could make this a requirement of the build script/image
RUN pip3 install --no-cache-dir --upgrade boto3 requests argparse

# set any other env variables
RUN mkdir build-task
ARG TASK_FOLDER
ADD $TASK_FOLDER build-task/
RUN export $(xargs <build-task/.env)

# run the custom build script
RUN build-task/build.sh

# copy common files, restructure
ADD common/ build-task/
RUN mv build-task/definition.py build-task/lib/definition.py

# this is always our entrypoint
ENTRYPOINT ["python", "build-task/main.py"]