# Use official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Ensure instance folder exists and is owned by user 1000
RUN mkdir -p /app/instance && chown -R 1000:1000 /app/instance

# Copy the current directory contents into the container at /app
COPY --chown=1000:1000 . /app

# Install any needed packages specified in requirements.txt
# We use --no-cache-dir to keep the image small
RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root user with ID 1000
RUN useradd -m -u 1000 user
# Switch to user 1000
USER user
# Set home to the user's home directory
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Run app.py when the container launches
CMD ["gunicorn", "-b", "0.0.0.0:7860", "app:app"]
