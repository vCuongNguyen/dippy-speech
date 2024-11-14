FROM python:3.12
COPY --from=ghcr.io/astral-sh/uv:0.4 /uv /bin/uv
ENV UV_SYSTEM_PYTHON=1
WORKDIR /app
#
# Install git and git-lfs
RUN apt-get update && apt-get install -y git git-lfs && rm -rf /var/lib/apt/lists/*

# Initialize git-lfs
RUN git lfs install

## Copy the requirements file into the container
COPY requirements_val_api.txt requirements.txt

RUN uv pip install -r requirements.txt

COPY voice_validation_api ./voice_validation_api
COPY scoring ./scoring
COPY utilities ./utilities
COPY model ./model
COPY constants ./constants
# Required for self installing module
COPY README.md .
COPY pyproject.toml .
COPY .git .git
RUN uv pip install -e .

COPY voice_validation_api/validation_api.py .

CMD ["python", "validation_api.py"]