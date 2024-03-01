FROM python:3.9

RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app/requirements.txt
COPY test_iss_tracker.py /app/test_iss_tracker.py

COPY . /app
RUN pip install -r /app/requirements.txt

ENTRYPOINT ["python3"]
CMD ["iss_tracker.py"]




