FROM python:3.12.3-bullseye

USER root

COPY src/ /app/
COPY requirements.txt /app/

RUN \
    pip \
        install \
            --no-cache-dir \
            --requirement \
                /app/requirements.txt

RUN \
    adduser \
        ppeagent

RUN \
    mkdir \
        -p \
            /app \
    && \
    chown \
        -R \
            ppeagent:ppeagent \
            /app

WORKDIR /app

USER ppeagent

ENV PPE_AGENT_IS_DOCKERIZED=1

CMD ["python", "serve.py"]
