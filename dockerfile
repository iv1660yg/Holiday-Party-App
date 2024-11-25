FROM python:3.9-slim

WORKDIR /app
RUN mkdir -p /app

COPY . /app

RUN pip install Flask

EXPOSE 5000

CMD ["python", "app.py"]
