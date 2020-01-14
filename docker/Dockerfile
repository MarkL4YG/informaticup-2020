FROM python:3.6

WORKDIR /usr/src/app

COPY python/ ./

RUN python3 -m pip install --no-cache-dir -r ./requirements.txt

COPY python ./
RUN mkdir -p /usr/src/app/output

VOLUME /usr/src/app/output

CMD ["python", "./main.py"]
