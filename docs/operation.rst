Operations Guide
================

This document describes the Dataset-driven staging flow used by the DRS3 DAGs.

Overview
--------

The pipeline is split into two DAGs:

- ``drs3_candidate_works_dataset``: producer/watcher DAG
- ``drs3_stage_works``: consumer/staging DAG

The producer checks for file content changes in:

- ``Path(STAGING_ROOT, "drs3_candidate_works.lst")``

When file content changes, the producer DAG:

1. Parses work IDs from the candidate file.
2. Calls ``populate_members(SRC_ROOT, work_names)``.
3. Stores a hash in Airflow Variable ``drs3_stage_works_candidate_hash``.
4. Emits Dataset event ``drs3://candidate_works/changed``.

The consumer DAG is scheduled on that Dataset and, when triggered,
fans out to 3 parallel tasks:

- ``stage_next_work_task_1``
- ``stage_next_work_task_2``
- ``stage_next_work_task_3``

DAG Contracts
-------------

Producer DAG
~~~~~~~~~~~~

- DAG ID: ``drs3_candidate_works_dataset``
- Schedule: every minute
- Behavior:

   - If candidate file is missing, unchanged, or empty: short-circuit
      (no Asset event)

   - If candidate file changed and has values: populate project members,
      then emit Asset event

Consumer DAG
~~~~~~~~~~~~

- DAG ID: ``drs3_stage_works``
- Schedule: ``[Asset("drs3://candidate_works/changed")]``
- Behavior:

  - Triggered by Dataset event from producer DAG
  - Executes up to 3 parallel ``stage_next_work_task`` runs

How To Test
-----------

1. Ensure Airflow services are healthy (scheduler, dag-processor, worker).
2. Put work IDs (one per line) into ``drs3_candidate_works.lst``.
3. Wait for the next producer poll interval (about 1 minute),
   or manually trigger the producer DAG.
4. In Airflow UI, confirm:

   - ``drs3_candidate_works_dataset`` run succeeds
   - Dataset event is emitted
   - ``drs3_stage_works`` is automatically triggered
   - Three stage tasks run in parallel

5. Re-run without changing file content: producer should short-circuit
   and no new consumer run should start.

Operational Notes
-----------------

- Dataset events are emitted by successful tasks with ``outlets``.
- Skipped tasks do not emit Dataset events.
- The hash Variable prevents duplicate work from unchanged files.
- If scheduling appears stalled, check scheduler health and logs first.

Pytest Invocation
-----------------

Use inline environment variables at invocation time so credentials
are not hardcoded:

.. code-block:: bash

   BDRC_DB_CNF="<fill_me>" BDRC_DB_PASSWORD="<fill_me>" pytest -q

For optional DB integration tests only:

.. code-block:: bash

   BDRC_DB_CNF="<fill_me>" BDRC_DB_PASSWORD="<fill_me>" pytest -q -m integration

.

Transitioning to Debian
=======================
This section logs the transition from the macOS development environment to
the Debian production environment.

Platform Preparation
--------------------
#. ``/var/lib/docker`` is the default Docker data root on Debian. On my host,
   it needed 10G free, so ``docker compose .... up -d`` gave me a shout
   about not enough space: docker requires 10G, only had 6.7G. I ran
   ``docker system prune -a --volumes`` to free up space, but for long term
   health, I wanted to move the Docker data root to a different partition.
   I didn't want to change the ``/`` partition. They don't recommend
   symlinking ``/var/lib/docker`` but it can be changed in
   ``/etc/docker/daemon.json``. So I changed it to point to a
   big-ass-partition: ``/vmnpool/data/docker``

#. groups
   - ``docker`` group is needed to run docker commands without sudo.
   - ``sudo usermod -aG docker $USER`` adds the current user to
   the docker group.

  .. code-block:: zsh

   # create group if missing
   sudo groupadd docker 2>/dev/null || true

   # add current user
   sudo usermod -aG docker "$USER"

   # verify socket group
   ls -l /var/run/docker.sock
   # should be root docker

   # apply new group in current shell
   newgrp docker

Build
-----
**Assumptions**
   See ``jimk@bodhi:/.oh-my-zsh/custom/aiases.zsh`` for the commands
   described here:

**d-comp**
   is an alias for ``docker compose``. It is used to avoid
   typing the space in ``docker compose`` with some specific
   docker compose files You just type ``d-comp`` followed by
   any docker compose sequence.

**dagup**
   restart the whole dag (using the complex of compose files)

**db-clup**
   Remove all history from the DRS3 database.safe -
   hardwired to work on QA only.

**dag-reset**
   Remove tmp files and restart the airflow-worker service.
   Useful to force reparse of code.

Methods
~~~~~~~
#. get ``github://drs-deposit`` (branch ``drs-deposit-DRS3``)
When you start from scratch, ``d-comp build`` from inside the repo working dir.
(to access ``.env`` and    ``secrets``)

#. Make all the host directories you need.

Artifacts
~~~~~~~~~
#. ``.env`` ``secrets`` You have to get these from a developer.
They're secrets, not handed out like candy.

Processing
~~~~~~~~~~
1. Running, airflow-apiserver was unhealthy. Copilot recommended:

.. code-block:: zsh

   docker compose ps
   docker compose logs --no-color --tail=300 airflow-apiserver
   docker inspect $(docker compose ps -q airflow-apiserver) --format '{{json .State.Health}}' | jq
   # Gives "Mode":"rw" for most, "Mode":"" for files in secrets. Mac is the same
   # Verify db dependencies
   docker compose logs --no-color --tail=200 postgres scheduler
   docker compose run --rm airflow-init
   docker compose up -d
   # Check API health from inside:
   docker compose exec airflow-apiserver sh -lc 'curl -fsS http://localhost:8080/health || wget -qO- http://localhost:8080/health'
   CID=$(docker compose ps -q airflow-apiserver)
   docker inspect "$CID" --format 'Exit={{.State.ExitCode}} Restart={{.HostConfig.RestartPolicy.Name}} Error={{.State.Error}}'
   docker inspect "$CID" --format '{{json .Mounts}}' | jq
   docker inspect "$CID" --format 'User={{.Config.User}} Entrypoint={{json .Config.Entrypoint}} Cmd={{json .Config.Cmd}}'

These are all helpful, but ``airflow-apiserver`` couldn't read  secrets.
Fix: ``chown -R 50000:0 ~/dev/drs-deposit/secrets``

2. No dags found
Since I'm not using the debug anymore, my ``docker-compose`` defined mounts in
the ``airflow-common`` section, but only had a subset of them defined in the
``airflow-worker`` section. First pass: Remove the entire ``volumes:``
section from ``airflow-worker`` and let it inherit from ``airflow-common``.

Basically, the host mount points have to be owned by ``50000:docker``,
or be a link, like ``/mnt/Archive[0-3]``

Ok, on Debian, I have the folders as 50000:0 on the host.
I
try the different - 50000:0 50000:jimk or 777?
I had thought that the `ao-workflows`` chaned ownerships on
/opt/airflow/dags, but it didn't. However the
ao-workflows/airflow-docker/deploy script **does**
make dags, logs, & etc 777. And I don't recall having to chown them.

Nope, that wasn't it. And I still need secrets
to be 50000 (I' running 777, so maybe I don't need the :0)
Nope, trying 755/jimk:jimk, but I noticed that
``secrets/airflow_jwt_secret.txt`` was 600.
So I changed it to 644, jimk:jimk, and the service came up.
It just couldn't read that one file.

Now, I need to be able to touch and edit dag files in place.
OK, so I've found out that running airflow under docker
actually changes thhe owner of
airflow files,

..code-block:: zsh

   drwxr-xr-x    - jimk  jimk 27 Jul 22:52  .vscode
   drwxrwxrwx    - 50000 root 27 Jul 22:52  config
   drwxrwxrwx    - 50000 root 29 Jul 18:37  dags
   drwxrwxr-x    - jimk  jimk 29 Jul 18:35  docs
   drwxrwxrwx    - 50000 root 29 Jul 18:37  logs
   drwxrwxrwx    - 50000 root 28 Jul 18:02  plugins
   drwxrwxrwx    - 50000 root 27 Jul 22:52  scripts
   drwxr-xr-x    - jimk  jimk 27 Jul 22:54  secrets
   drwxrwxr-x    - jimk  jimk 27 Jul 22:52  tests
   drwxrwxrwx    - 50000 root 29 Jul 18:37  utils

So, the next thing to do is to write a deploy script,
like for the ``ao-workflows`` repo, that will chown the dags,
logs, and plugins to 50000:0

Deploy Sync Helper
------------------

**Name**
   ``deploy_project.sh`` - A project deployment script to copy only the
   runtime deploy set needed to run docker compose from the target directory:

- ``.env``
- ``Dockerfile``
- ``Dockerfile.dev``
- ``docker-compose.yaml``
- ``docker-compose-dev.yaml``
- ``docker-compose-secrets.yaml``
- ``dags/``
- ``plugins/``
- ``scripts/``
- ``utils/``

You can use a local target path or an rsync remote target
(``user@host:/absolute/path``).

For remote deploys without sudo privileges, ownership normalization on
``secrets/`` now falls back automatically:

- first try ``chown`` to ``${AIRFLOW_UID:-50000}:0``
- then try ACL via ``setfacl`` (if available) **This really works**
- finally apply readable permissions (``755`` on dirs, ``644`` on files)

If the remote path is already known to exist, you can skip the initial
SSH mkdir precheck:

.. code-block:: zsh

   ./scripts/deploy_project.sh jimk@bodhi:/home/jimk/dev/ao-workflows/airflow-docker/deploy --delete --no-ssh-precheck

Standard one-liner:

.. code-block:: zsh

   ./scripts/deploy_project.sh /home/jimk/dev/ao-workflows/airflow-docker/deploy --delete

Common variants:

.. code-block:: zsh

   # Preview changes only
   ./scripts/deploy_project.sh /home/jimk/dev/ao-workflows/airflow-docker/deploy --dry-run

   # Sync (secrets ownership normalization is applied automatically)
   ./scripts/deploy_project.sh /home/jimk/dev/ao-workflows/airflow-docker/deploy --delete
