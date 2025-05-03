FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y libgl1

# Set workdir
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose port
EXPOSE 8080

# Run the app
CMD ["python", "main.py"]