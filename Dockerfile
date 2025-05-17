FROM ubuntu:22.04

# Set non-interactive installation
ENV DEBIAN_FRONTEND=noninteractive

# Install Python and minimal packages in one layer
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-numpy \
    python3-pandas \
    && rm -rf /var/lib/apt/lists/*

# Install minimal NSJail dependencies in a single layer
RUN apt-get update && apt-get install -y \
    git \
    bison \
    flex \
    gcc \
    g++ \
    make \
    pkg-config \
    libnl-route-3-dev \
    libprotobuf-dev \
    protobuf-compiler \
    && rm -rf /var/lib/apt/lists/*

# Build NSJail
RUN cd /tmp \
    && git clone --depth=1 https://github.com/google/nsjail.git \
    && cd nsjail \
    && make -j$(nproc) \
    && cp nsjail /usr/local/bin/ \
    && cd / \
    && rm -rf /tmp/nsjail

# Install lightweight Python dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py executor.py nsjail.cfg ./

# Expose the port
EXPOSE 8080

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]