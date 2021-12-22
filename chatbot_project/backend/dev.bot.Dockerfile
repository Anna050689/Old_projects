FROM python:3.9

WORKDIR /usr/src/app

RUN pip install pipenv

COPY Pipfile .
COPY Pipfile.lock .

RUN pipenv install --dev

COPY . .

CMD ["pipenv", "run", "python", "bot.py"]
