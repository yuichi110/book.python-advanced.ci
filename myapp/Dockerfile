FROM python:3.10-alpine AS production
WORKDIR /app
COPY pyproject.toml /app
RUN pip install .
COPY myapp /app/myapp
CMD ["uvicorn", "myapp.main:app", "--host", "0.0.0.0", "--port", "80"]

FROM production AS test
RUN pip install .[test]
COPY tests /app/tests
