FROM python:3.11-slim

WORKDIR /app

# System dependencies required by matplotlib/pandas wheels on slim images
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

# Runs the interactive cluster explorer by default.
# Override the command (e.g. `jupyter notebook`) to work with the analysis notebook instead.
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
