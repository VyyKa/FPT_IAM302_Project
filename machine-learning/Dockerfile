# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.12.7-bullseye

# Expose the necessary port
EXPOSE 8001

# Environment variables
# Prevents creation of .pyc files
ENV PYTHONDONTWRITEBYTECODE=1 
# Turns off buffering for easier logging
ENV PYTHONUNBUFFERED=1

# Create and activate a virtual environment
RUN python -m venv /opt/venv

# Set working directory for api and copy files
WORKDIR /app
COPY api /app
COPY MLMAP /MLMAP

# Install requirements
RUN /opt/venv/bin/python -m pip install --upgrade pip && \
    /opt/venv/bin/pip install -r /MLMAP/requirements.txt && \
    /opt/venv/bin/pip install -r /app/requirements.txt && \
    /opt/venv/bin/pip install gunicorn

# Creates a non-root user with an explicit UID and grants access to /app
RUN adduser --uid 5678 --disabled-password --gecos "" appuser && \
    chown -R appuser /app

USER appuser

# Update PATH to use the virtual environment as default for CMD
ENV PATH="/opt/venv/bin:$PATH"

# Start the application
CMD ["gunicorn", "--bind", "0.0.0.0:8001", "app:app"]
