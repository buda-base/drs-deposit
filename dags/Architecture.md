# DRS3 population and tracking
## Environment
This project runs as DAGs in the airflow environment. Refer to `docker-compose[-dev].yaml` `Dockerfile` for the details. a DAG in this document means an airflow dag. Refer to the containing project.
## Sources
- The source root is local machine, `~/tmp/DRS3/Archive`
- The staging root is local machine, `~/tmp/DRS3/staging`
- Create these roots as volumes in the `docker-compose-dev.yaml` for the airflow worker processes
### Database
- The database is located by using the Python package `BdrcDbLib.DrsContext.DrsDbContext('qa')`. This opens the DRSQA database. 
- The orm for the database is in the Python project `BdrcDbModels`
- General note: Beware of having multiple threads open the DrsDbContext. When creating and updating an object, close the database connection while the task is being updated. This means that the steps below, have to save a record's id while the step is being processed, and then only reopen the database connection, update the entry, commit, and leave.

## Shared Patterns
### Tracking
- The entities in the BdrcDbModels.project_manager module track the processing. In each task that processes an entry, the task will use the DrsDbConnection('qa') connection context to perform the query specified in the task, whether that is to search, or create a new object (usually a ProjectMemberStep object, which records the steps an object goes through) and then exit the context.

- In each task that processes an object, two calls are required:
    - create the ProjectMemberStep (PMS), fill in the project, member, and step id, and commit. This saves the new PMS id into the task's variables. Exit the context.
    - When the task completes, fetch the PMS by id, and update it with the task end time and task result. Do this in a finally block

### Paths

## Populate the ProjectMembers
- Write a dag that uses a dataset, which is the set of works which the DAG will process. The dataset will be populated from a text file initially. The enclosing DAG will sense changes in this dataset, and will run when it detects a change in the contents - use airflow dataset methods to detect those changes.
- for each entry in the Dag's list:
    - locate it using the `https://github.com/buda-base/bdrc-utils/archive-ops.shell_ws.get_mappings(). Use the root `~/tmp/DRS3/Archive` as the root argument.
    - Create a ProjectMember db record for it, with the attributes:
        - member type = `work` 
        - workId is the `Work.workId` where `Work.WorkName` == work_name (which is the last node in the work's path)
    - For each directory under the work's `images/` directory:
        - Create a ProjectMembers entry for that directory, with a MemberType of Volume, using the volumeId and related workId. Look up the volume id in `Volumes` and the workId from the Volume's WorkId

## Create a DAG to stage works
- Query the DB for ProjectMembers of type 'Work' that have no child volumes (ProjectMembers of type 'volume' join workId on PM(Work).workId) that have any ProjectMemberSteps child record. Take 1 only. Create a ProjectMemberStep for the volume of type 'staged' and update the database.

- for the result:
    - set the output directory to staging root/WorkNumber 
    - invoke drs_utils.stage_content with the located work's path (see "Populate the ProjectMembers above).
    - Update the volume's ProjectMemberStep entry for the volume. It's step attribute will be ProjectSteps('DRS3','staged')        
- Detect if all the work's volumes have been staged: If they have (all ProjectMembers whose work id is the work's workId will have a projectmemberstep record of 'staged' that has been successfully completed), create a ProjectMemberStep record for the work, with the ProjectStep('DRS3', 'staged')'

## Create a DAG to process the staged entries
### Start task. Get the next staged entry that hasn't been further processed.

- Use the database to detect new staged entries. SqlAlchemy query for the oldest ProjectMember of member_type `work` that has no ProjectMemberStep of 'staged.' ProjectMember When the ProjectMember is located, create a ProjectMemberStep for it  that has 
     - the current time as the project_member_step_start_time, 
     - the project_step_id for 'staged' and update the database with it. 
- Save the ProjectMemberStep, including its id (commit the creation). and the workId in the task context array. Downstream tasks will use these as inputs.

### Transcode the staged entries
- Create another DAG whose initial step queries ProjectMemberSteps that have member type 'work and step 'staged', and do not have a ProjectMemberStep of 'transcode' Note this implies that all its child volumes are staged, and not transcoded. For the returned entry:
    - Mark the entry's PMS with the transcode Project_step_id.
    - update and commit the PMS
    - Fetch all the ProjectMembers whose work id is the same as the returned entry's work id, and whose membertype is volume, and whose projectmemberstep project_step_id is staged, and the ProjectMemberStep has a non-null project_member_step_end_time and a project_member_result_code of 0. This represents all the Volumes that have been successfully staged.
    - transcode each volume with  drs_pds_transcode.transcode() When each object starts, create a ProjectMemberStep for it, with a step_type of 'transcode (use the FK).
    - When each volume's transcode step ends, mark its PMS with the end time and the result code (as above). commit the update.
### Generate metadata for the staged entry
- After the transcode tasks are complete, generate a task that invokes drs_utils.create_metadata_file to create the metadata file for the work as a whole. Save the path that in the airflow context

### Transmit the work
- Create PMS entries for the work and all its volumes that has the project_step_id for 'upload'
- Invoke drs_utils.send_to_s3
- On failure, delete the work and its volumes from the remote site. 
- If successful, upload the metadata file generated in the previous step
- Update the PMS entries for the work and its volumes with the complete time and  status. Use a finally block.

# Enhancements
Good first try
Next, we will look at:
- exception handling - somehow, we have to figure out what to unwind. Each step, when an exception, has to set the appropriate steps to failure state.
- Also has to signal airflow failure

