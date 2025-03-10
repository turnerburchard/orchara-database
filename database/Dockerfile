FROM postgres:13

# Install build tools and PostgreSQL development files
RUN apt-get update && apt-get install -y \
    build-essential \
    postgresql-server-dev-13 \
    git

# Clone, build, and install pgvector
RUN git clone https://github.com/pgvector/pgvector.git /pgvector && \
    cd /pgvector && \
    make && make install && \
    cd / && rm -rf /pgvector && \
    apt-get remove -y build-essential postgresql-server-dev-13 git && \
    apt-get autoremove -y && rm -rf /var/lib/apt/lists/*
