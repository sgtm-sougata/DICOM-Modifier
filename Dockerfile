
# Use Python base image
FROM python:3.8

# Set working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app.py file to the container
COPY app.py .

# Expose the port for Streamlit (8501 is the default Streamlit port)
EXPOSE 8082

# Command to run the Streamlit app
CMD ["streamlit", "run", "app.py"]
