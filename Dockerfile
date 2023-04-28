FROM python:3.11
# Use the python latest image
COPY . ./
# Copy the current folder content into the docker image
RUN pip install --no-cache-dir -r requirements.txt
# Install the required packages of the application
CMD exec gunicorn --bind :$PORT --workers 1 --worker-class uvicorn.workers.UvicornWorker  --threads 8 main:app
# Bind the port and refer to the app.py app