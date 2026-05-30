
FROM python:3.14-alpine
WORKDIR /plane_scanner_app
COPY requirements.txt .
RUN apk add --no-cache gcc musl-dev linux-headers libffi-dev git \
    && pip install --no-cache-dir -r requirements.txt
COPY . .

CMD ["python","-u", "app/main.py"]