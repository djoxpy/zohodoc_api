FROM python:3.12
WORKDIR /usr/src/zohodoc_api
RUN mkdir ./csv
RUN mkdir ./downloads_xlsx
COPY .env .
ADD https://github.com/djoxpy/zohodoc_api.git ./
RUN pip install -r requirements.txt
CMD ["python", "./run.py", "--first", "--interval", "12", "start"]
