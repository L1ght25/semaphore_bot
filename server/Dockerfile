FROM python:3.10.4-slim
WORKDIR /server
COPY . .
RUN pip install --no-cache-dir --upgrade pip
EXPOSE 8000
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

CMD [ "python3", "Server.py" ]