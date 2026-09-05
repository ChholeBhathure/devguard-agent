# 1. Base Image: Use an official lightweight Python runtime
FROM python:3.10-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy project definition and source code
COPY pyproject.toml .
COPY src/ src/

# 4. Install Devguard into the container environment
RUN pip install --no-cache-dir .

# 5. Define the default entrypoint command
ENTRYPOINT ["devguard"]