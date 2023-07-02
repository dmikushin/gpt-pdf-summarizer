# Use an official Python runtime as a parent image
FROM python:3.9

LABEL maintainer="dmitry@kernelgen.org"
 
ENV DEBIAN_FRONTEND=noninteractive

# Run the command to start the FastAPI app
RUN apt update && \
    apt -y --no-install-recommends install \ 
        supervisor

# Set the working directory to /app
WORKDIR /app

# Install Poetry
RUN pip install poetry openai langchain

# Copy pyproject.toml and poetry.lock files into the container
COPY pyproject.toml poetry.lock /app/

# Install dependencies
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi \
  && poetry shell

# Copy the application
COPY app /app/app

# We use supervisord to run multiple executables in the Docker container
COPY ./supervisord.conf /etc/
COPY ./supervisor-log-prefix.sh /

# Make port 8000 available to the world outside this container
EXPOSE 8001
EXPOSE 8501

# Set environment variables
ENV PYTHONUNBUFFERED=1

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
