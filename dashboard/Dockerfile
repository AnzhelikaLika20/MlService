FROM python:3.11-slim

WORKDIR /dashboard

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["streamlit", "run", "dashboard.py"]
