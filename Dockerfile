FROM python:3.12
ADD run.py tables_comparsion.py tg_api.py requirements.txt zoho_api ./
RUN pip install requests beautifulsoup4 python-dotenv
CMD [“python”, “./main.py”] 