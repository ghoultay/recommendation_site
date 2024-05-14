# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y gcc && \
    apt-get clean

# Create and activate a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port your app runs on
EXPOSE 8000

# # Run database migrations
# RUN python movierec_site/manage.py migrate

# # Collect static files
# RUN python movierec_site/manage.py collectstatic --noinput

# Run the application
CMD ["python", "./movierec_site/manage.py", "runserver", "0.0.0.0:8008"]