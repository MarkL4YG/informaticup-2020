FROM python:3

WORKDIR /usr/src/app

COPY python/ ./

RUN pip install --no-cache-dir -r ./requirements.txt

COPY python ./
RUN mkdir -p /usr/src/app/output

VOLUME /usr/src/app/output

CMD ["python", "./main.py"]
