FROM python:3.13.3-slim-bullseye

WORKDIR /app

# install build tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl && \
    rm -rf /var/lib/apt/lists/*

# install rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy the rest of the app
COPY . .

# non root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser