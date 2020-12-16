#Get the base images
FROM python:3.9.0 AS develop-stage
#Install and update dependancy for staticx
RUN apt update && apt install patchelf
#Set the working directory
WORKDIR /app
#Set some python env vars
ENV PATH="/venv/bin:$PATH"
ENV PYTHONPATH=/app
#Create the virtual env for python to isntall modules
RUN python -m venv /venv
#Copy over the requirements txt for pip
COPY SimproToTTM/requirements.txt requirements.txt
#install python dependencies
RUN pip install --no-cache-dir -r requirements.txt
#Copy over the application source to the /app folder in the container
COPY SimproToTTM/. .
#Entry command for this stage
CMD ["python", "main.py"]

#Pull from the previous state
FROM develop-stage as build-stage
#Make a tmp dir this is needed for pyinstaller to use
RUN mkdir tmp
#Make a storage dir this is for logs etc
RUN mkdir /app/storage
#Copy python dependencies from previous venv
COPY --from=develop-stage /venv /venv
#run pyinstaller to make a one-file bundled executable of the app
RUN pyinstaller -F main.py
#run staticx to grab a linux dependencies and make a package of it. the -l is adding a library that concurrent futures needs
RUN staticx -l /lib/x86_64-linux-gnu/libgcc_s.so.1 /app/dist/main /app/dist/main_tmp
#Entry command for this stage
CMD ["/app/dist/main"]

#New base image with nothing in it
FROM scratch
#Create a non admin user
USER 65535
#Copy tmp files and set user permissions
COPY --from=build-stage --chown=65535:65535 /app/tmp /tmp
#Copy the staticx application and set user permissions
COPY --from=build-stage --chown=65535:65535 /app/dist/main_tmp /app/main
#Copy the storage dir
COPY --from=build-stage --chown=65535:65535 /app/storage /app/storage
#Entry command for this stage
CMD ["/app/main"]