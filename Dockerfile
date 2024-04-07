FROM python:3.10

ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt

COPY start-server.sh /app/start-server.sh
RUN chmod +x /app/start-server.sh

EXPOSE 8000

ENTRYPOINT ["/app/start-server.sh"]
