FROM python:3.10-alpine AS test
WORKDIR /app
COPY pyproject.toml /app
RUN pip install .
RUN pip install .[test]
COPY myapp /app/myapp
COPY tests /app/tests
CMD ["uvicorn", "myapp.main:app", "--host", "0.0.0.0", "--port", "80"]

FROM python:3.10-alpine AS production
WORKDIR /app
COPY pyproject.toml /app
RUN pip install .
COPY myapp /app/myapp
CMD ["uvicorn", "myapp.main:app", "--host", "0.0.0.0", "--port", "80"]


