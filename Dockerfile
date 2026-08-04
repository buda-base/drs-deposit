FROM apache/airflow:3.2.1

USER root
RUN mkdir -p /mnt/staging/DRS3
RUN mkdir -p /mnt/Archive0
RUN mkdir -p /mnt/Archive1
RUN mkdir -p /mnt/Archive2
RUN mkdir -p /mnt/Archive3
RUN chown -R airflow:root /mnt/staging/DRS3
RUN chown -R airflow:root /mnt/Archive0
RUN chown -R airflow:root /mnt/Archive1
RUN chown -R airflow:root /mnt/Archive2
RUN chown -R airflow:root /mnt/Archive3

USER airflow

COPY --chown=airflow:root --chmod=755 scripts/load_secret_env.sh /opt/airflow/scripts/load_secret_env.sh

RUN pip install --no-cache-dir \
    "bdrc-db-models>=2.0.6" \
    "bdrc-db-lib2>=2.0.6" \
    "cryptography>=47.0.0" \
    "pillow>=12.2.0" \
    "s3pathlib>=2.3.6" \
    "tqdm>=4.67.3" \
    "bdrc-util2>=2.0.6"
