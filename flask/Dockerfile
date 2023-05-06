FROM python:3.8.16

COPY ./requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
RUN rm /tmp/requirements.txt

WORKDIR /app

ENTRYPOINT ["python3"]
CMD ["app.py"]