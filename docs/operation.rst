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
This section logs the transition from the macOS development environment to the Debian production environment.

Platform Preparation
--------------------
#. ``/var/lib/docker`` is the default Docker data root on Debian. On my host, it needed 10G free, so ``docker compose .... up -d`` gave me a shout 
about not enough space: docker requires 10G, only had 6.7G. I ran ``docker system prune -a --volumes`` to free up space,
but for long term health, I wanted to move the Docker data root to a different partition. 
I didn't want to change the ``/`` partition. They don't recommend symlinking ``/var/lib/docker`` 
but it can be changed in ``/etc/docker/daemon.json``. So I changed it to point to a big-ass-partition: ``/vmnpool/data/docker``

#. groups 
   
   - ``docker`` group is needed to run docker commands without sudo. 
   - ``sudo usermod -aG docker $USER`` adds the current user to the docker group. 

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

   See ``jimk@bodhi:/.oh-my-zsh/custom/aiases.zsh`` for the commands described here:
**d-comp**
   is an alias for ``docker compose``. It is used to avoid typing the space in ``docker compose`` with some specific 
   docker compose files You just say ``dcomp ``__any docker compose sequence__

**dagup**
   restart the whole dag (using the complex of compose files)

**db-clup** 
   Remove all history from the DRS3 database.safe - hardwired to work on QA only  

**dag-reset**
   Remove tmp files and restart the airflow-worker service. Useful to force reparse of code.

Methods
^^^^^^^
#. get ``github://drs-deposit`` (branch ``drs-deposit-DRS3``)
When you start from scratch, ``d-comp build`` from inside the repo working dir.
(to access ``.env`` and    ``secrets``)

#. Make all the host directories you need.

Artifacts
---------
#. ``.env`` ``secrets`` You have to get these from a developer. They're secrets, not handed out like candy.

Processing
----------
1. Running, airflow-apiserver was unhealthy. COpilot recommended:

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
the ``airflow-common`` section, but only had a subset of them defined in the ``airflow-worker`` section.
First pass: Remove the entire ``volumes:`` section from ``airflow-worker`` and let it inherit from ``airflow-common``.  

Basically, the host mount points have to be owned by 50000:docker (or be a link, like ``/mnt/Archive[0-3]``




