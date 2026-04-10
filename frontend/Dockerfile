FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy frontend code
COPY . .

# Environment variables (provided at runtime)
ENV PORT=8501
ENV BACKEND_URL=http://backend:8000

# Start command
CMD streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0
