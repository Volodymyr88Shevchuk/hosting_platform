FROM python:3.11-slim

WORKDIR /app

COPY app/app.py /app/app.py
COPY app/static /app/static
RUN pip install --upgrade pip
RUN pip install fastapi uvicorn python-multipart

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
