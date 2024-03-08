FROM python:3.9

RUN mkdir /ISSTracker
WORKDIR /ISSTracker

COPY . /ISSTracker
RUN pip install -r /ISSTracker/requirements.txt

ENTRYPOINT ["python3"]
CMD ["iss_tracker.py"]




