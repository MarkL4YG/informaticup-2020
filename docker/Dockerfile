FROM python:3

WORKDIR /usr/src/app

COPY ../python/requirementx.txt ./

RUN pip install --no-cache-dir -r ./requirements.txt

COPY ../python ./

CMD ["python", "./main.py"]
