FROM python:3.11-slim-bullseye

COPY requirements.txt /requirements.txt
RUN pip install --index-url http://pypi.bar.local --trusted-host pypi.bar.local -r /requirements.txt

COPY RankingsAPI /RankingsAPI

ENTRYPOINT ["python", "-um", "RankingsAPI"]
