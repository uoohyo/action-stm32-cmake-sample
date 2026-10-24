# Automation validation and operating boundaries

Run the non-vendor regression checks with `python3 -m unittest discover -s tests -v`.
They do not download or install TI/ST software. The `Validate Automation` PR check
covers scripts and template consistency; version-specific workflows remain explicitly
dispatchable for real toolchain tests.

## Trigger and release contract

Project changes run the affected version tests. Changes to a generated workflow,
its template, or shared test helpers also run the corresponding main-branch tests.
README/result-only changes do not start compiler jobs. Generated workflow changes
are deliberate test inputs, not silently excluded to reduce execution counts.
The maintenance workflow runs on main and uses a PR dry-run without publishing.
Its renamed identity restores an active schedule without modifying repository settings.

## Maintenance authentication

Workflow publication still requires the existing `PAT_TOKEN` with repository Contents
and Workflows write permissions and a compatible branch policy. No secret or permission
is changed by this patch. The push uses a short-lived askpass script and an explicit
GitHub URL instead of relying on inherited checkout authentication. Token validity,
permissions, and protected-branch behavior must be verified by an authorized main-branch
maintenance run with actual changes. PR checks do not prove production push access.

## Result interpretation

Every configuration records schema version 2, version, configuration, run ID, attempt,
main/feature branch, and head SHA. A version passes only when Debug and Release from
the exact selected run attempt both pass and the workflow succeeds. The collector selects
the latest completed main-branch push or manual run per generated workflow, not an arbitrary PR run.
Partial failed-job reruns deliberately do not mix evidence across attempts: rerun all
jobs to obtain a complete two-configuration result for one attempt.
An in-progress newer run does not erase the last completed result; its recorded SHA and
run timestamp remain visible. This is not a claim that every version tested the latest
README-only commit.

Missing, legacy, incompatible, or inaccessible artifacts replace old success records
with explicit missing evidence. README status, configuration outcomes, SHA, timestamp,
and log link describe the same fixed run. An incomplete collection updates that state
and then fails visibly. Existing Debug-only artifacts are intentionally not upgraded to
complete evidence; each version needs a new two-configuration run after migration.

## Real-build verification still required

Static/fixture tests do not establish vendor toolchain compatibility. After approval,
run representative version workflows on the final commit and inspect both configurations.
Then verify a maintenance run can publish generated files and a result synchronization
run can collect both artifacts. Do not close operational issues solely because this PR
passes its unit tests.

## STM32 support matrix

The checked-in project targets STM32F103C8T6 using the existing CMake presets on
Ubuntu GitHub-hosted runners. Passing this fixture does not cover all custom generator,
quoted argument, Programmer, or hardware programming configurations.
