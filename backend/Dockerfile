# Dockerfile — packages the BoulderIQ backend into a self-contained image.
#
# Build with:   docker build -t boulderiq-backend .
# Run with:     docker run -p 8000:8000 boulderiq-backend
# Then visit:   http://127.0.0.1:8000/docs   (same as running uvicorn directly)

# Start from an official, small Python base image (slim = fewer unnecessary
# OS packages, smaller image size, faster builds/pulls)
FROM python:3.13-slim

# All following commands run from /app inside the container
WORKDIR /app

# Copy ONLY requirements.txt first, before the rest of the code.
# Why: Docker caches each step. If only your .py files change (not
# requirements.txt), Docker reuses the cached "pip install" step instead
# of re-downloading every package on every build -- much faster iteration.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the actual application code
COPY . .

# Document that this container listens on port 8000 (informational --
# doesn't actually open the port by itself, -p at `docker run` does that)
EXPOSE 8000

# The command that runs when the container starts.
# --host 0.0.0.0 is REQUIRED here (not 127.0.0.1): inside a container,
# 127.0.0.1 only means "inside this container", so the outside world
# (your Mac, or the cloud) couldn't reach it. 0.0.0.0 means "listen on
# all network interfaces", which lets the port mapping actually work.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
