FROM python:3.11-slim

WORKDIR /app

COPY app /app

RUN pip install --upgrade pip
RUN pip install fastapi uvicorn python-multipart passlib[bcrypt] python-jose

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
