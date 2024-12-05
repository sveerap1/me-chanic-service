FROM python:3.10-slim

WORKDIR /app
COPY . /app

# RUN pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org pip setuptools
# RUN apt-get update && apt-get install -y libpq-dev build-essential

RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "mebot.main:app", "--host", "0.0.0.0", "--port", "8000"]
