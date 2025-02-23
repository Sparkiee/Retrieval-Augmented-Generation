FROM python:3.10

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt . 
RUN pip install -r requirements.txt

# Download the spaCy model
RUN python -m spacy download en_core_web_sm

# Copy the rest of the app
COPY . .

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
