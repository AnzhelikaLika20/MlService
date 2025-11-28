FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install streamlit
COPY . /app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
