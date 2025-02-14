FROM python:3.12
ADD git@github.com:djoxpy/zohodoc_api.git ./
RUN pip install -r requirements.txt
CMD [“python”, “./run.py”]