# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /code

# Copy the dependencies file to the working directory
COPY ./requirements.txt /code/requirements.txt

# Install any needed dependencies specified in requirements.txt
# This runs inside the clean container, away from the local machine's conflicts.
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the Firebase Admin key needed to connect to the database
COPY ./firebase-service-account.json /code/firebase-service-account.json

# Copy the Google credentials needed for the Calendar API
COPY ./credentials.json /code/credentials.json
COPY ./token.json /code/token.json

# Copy the local code to the container
COPY ./app /code/app
COPY ./main.py /code/main.py

# Expose the port Cloud Run will use
EXPOSE 8080

# Run the command to start the server using a shell to process the $PORT variable
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
