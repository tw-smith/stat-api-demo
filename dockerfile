FROM python:3.12

EXPOSE 8000

WORKDIR /app

# Install dependencies
COPY . .

RUN pip3 install poetry 
RUN poetry config virtualenvs.create false
RUN poetry install --with dev

# Run your app
CMD ["gunicorn","api.application:app", "--bind","0.0.0.0:8000","--workers","4","--worker-class","uvicorn.workers.UvicornWorker","--timeout","120"]

# To run, set an env variable named TOKEN and run the following command:
# docker run -d -p 8000:8000 -e TOKEN ocstapi