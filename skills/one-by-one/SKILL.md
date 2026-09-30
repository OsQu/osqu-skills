---
name: one-by-one
description: Execute work in small, user-verified increments with a stop-and-commit gate after each task. Use when the user wants close control of an implementation; not for autonomous execution.
---

# One By One

Use this workflow when the user wants to review each discrete change before the next one begins.

## Start

1. Explore the relevant code and constraints before proposing implementation work.
2. Ask a concise question when a material decision cannot be safely inferred. Do not begin mutations that depend on the answer.
3. Break the request into independently reviewable tasks. State the current task, its expected outcome, and its verification command before changing files.
4. Create or update `{{tasklog_dir}}/PROJECT_NAME-TASKLOG.md` before implementation, replacing `PROJECT_NAME` with the project's name so each project has its own log. Reuse the same filename when resuming that project. Record the planned tasks and mark the current task as in progress.
5. Use `{{planning_doc_dir}}` for new planning documents when needed, unless the project or user specifies another location. Reuse existing planning documents in their established locations.

## Per-task loop

1. Implement only the current task. Do not start later tasks or opportunistically expand scope.
2. Run the smallest relevant verification. Run required repository checks when applicable.
3. Update the task log with the changes, verification commands and results, known limitations or blockers, and current status. Mark implemented work as awaiting user verification; record completion only after the user verifies it. Preserve earlier entries so the log supports resuming work.
4. Report the changed files, verification result, and any known limitation, including the task log's location.
5. Stop and wait for the user to verify and explicitly authorize the next task. The user controls commits; do not commit or push unless they specifically ask.

Treat every task boundary as a hard gate. A request to continue begins the next task; a request to revise applies only to the current task unless the user says otherwise.

## Scope

This is the deliberate, highest-control mode. It does not authorize subagents, parallel work, autonomous multi-task execution, commits, pushes, or external actions beyond the user's request. Add other operating modes as separate, explicitly named skills or as explicit modes in a future revision; never infer a more autonomous mode from this skill.
