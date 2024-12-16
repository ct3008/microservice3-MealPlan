# Use the official Python image
FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Expose the port your FastAPI app runs on
EXPOSE 5002

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5002", "--reload"]