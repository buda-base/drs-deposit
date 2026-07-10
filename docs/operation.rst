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
