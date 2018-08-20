# Related Files Design
## Overview
### Purpose of this Document
RelatedFilesDesign.md enumerates the changes needed to the BDRC DRS system to support related files.
### Intended Audience
This document is intended for technical personnel who work with BDRC assets at the information systems level. It describes changes to database schemas, shell and Python scripts, and refers to internal BDRC storage.
## DRS Related Files
On Harvard's DRS item viewer (for example, their (QA Mirador viewer for Object ID 401878810)[https://iiiftest.lib.harvard.edu/manifests/view/drs:401878810]), the menu contains an item for 'Related Links'

![Related Links](images/2018/08/related-links.png)

The related links for an object are specified in the batch build for that object. They can be any URI, but in our case, we only link two very specific DRS objects (where the work has one):
* The Outline for the work (not all works)
* The Print Master file for the work.

The builder of the DRS object can specify any number of related links in the batch's `project.conf.` This means that the target of the link (the URL the link references) **must be specified at batch build time**
DRS has no web service API for updating a built batch or deposited documents.
## Implementation
### Existing workflow
See 'DRS Workflows' below for data flow.
The existing workflow contains three separate, yet equally important, modules:
* Batch Building Workflow
* Record Deposit Status Workflow
* Deposit Workflow
![DRS Workflows](images/2018/08/drs-workflows.png)

The salient point in the existing workflow is that the URNs for a related file for a batch refer to DRS objects which have already been deposited. The DRS process creates those URNS, and the `DRSUpdate` module adds them to the database, which is the data source for `getReadies`

### Changes to existing workflow

Related files only changes the Batch Building Workflow. The other workflows, 'Record Deposit Status Workflow', and 'Deposit Workflow' already support related files (once a batch has been built, the deposit process is the same for all content models). Changes are required for:
* Creating batches for related Files
* Associating related files with the batch builds which reference them
#### Creating batches for related Files
The batch building process so far is tailored to a DRS content model named  PDS Document, which arranges a collection of files into an object which a browser can page through. Print Masters and outlines are a different content model: only one file per object. Outlines are instances of the TEXT content model (Unicode text), while PrintMasters are the DOCUMENT object (one PDF file, containing multiple internal pages).
##### Low level build scripts
For this reason, we'll have to add another low level batch building program will need creation. Ideally, it might support both Outlines and Print Masters, but that is an option, not a requirement - we could create separate routines for each content model. These routines will require:
* Options to `getReadies`: we need to build a separate batch building stream for related files, and for the files they relate to. `getReadies` needs to pass an argument to the database which restricts is domain of inquiry to either Works, or to Outlines or PrintMasters.
* `project.conf` template (the source from which we create batch building projects)
### Changes to database
Currently, the tables `Outlines` and `PrintMasters` are placeholders which only hold foreign key relationships to `Works` Since the rewrite conceives of Outlines and Print Masters as ordinary DRS deposit objects, they can be stored in the `Volumes` table. The `Outlines` and `PrintMasters` tables become child tables of `Volumes`
* Add routines `AddOutline` and `AddPrintMaster` similar to `AddVolume` (Like volumes, Outlines and Printmasters are primarily read-only - they will only changed when BDRC adds works to its catalog: once added, they are intended to be invariant)
* Change the definition of `AllReadyWorks` view to not reference the Outlines table relative to works: use a left join on Volumes
* The `Volumes.label` field for outlines will support a naming convention (**which the code must not exploit!**) of '_<WorkName>_- Outline' and '_<WorkName>_- PrintMaster'. Code should not depend on this - it is simply that the `label` name has a unique index, and we need to create both Outline and PrintMaster labels for a work.
* Extend the logic of the routine `GetReadyVolumes` to restrict the scope to outlines, print masters, or works. Use that to determine which table to join with to filter the results.
