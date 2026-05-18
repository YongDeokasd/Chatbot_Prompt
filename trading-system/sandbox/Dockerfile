FROM python:3.11-slim

WORKDIR /sandbox
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY runner.py .

# Executed by backend via Docker Socket Mount with hard limits (§9.1):
#   --network none --memory 256m --cpus 0.5 --read-only
#   --user nobody --pids-limit 50 --cap-drop ALL --rm
USER nobody
ENTRYPOINT ["python", "runner.py"]
