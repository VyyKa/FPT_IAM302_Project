# Web UI/API for the project

This is the web UI/API for the project. It is a simple web application that allows users to interact with the project.

## Running the web UI/API

To run the web UI/API, you need to have the following installed:

- Docker

To run the web UI/API, run the following command:

```bash
# https://hub.docker.com/r/cybersecn00bers/file-uploader
docker run -d --rm --name  file-uploader --network host -v $(pwd)/web_db:/app/instance cybersecn00bers/file-uploader
```
