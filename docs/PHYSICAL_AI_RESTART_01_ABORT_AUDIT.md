# restart_01 aborted partial-collection audit

Scientific freeze: `1a4d748`. Execution: `restart_01`.

Nine persisted metadata records and nine corresponding raw response files are
present. Each persisted record has `attempt_number = 1`; there are no duplicate
candidate IDs and no orphan raw files. No evaluator, parser, or scientific
metric was run.

The execution was stopped because the launcher and child Python processes
remained active after the controlling execution returned. The runner is
sequential, but its parent/subprocess invocation was not joined by the
external controller. Because a request could have been in flight when the
processes were terminated, the transmitted-request count is conservatively
classified as **MORE THAN 9 POSSIBLE**. `restart_01` is excluded from all
confirmatory analysis.
