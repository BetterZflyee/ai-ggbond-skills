# X Followings Digest Cronjob Export & Pause Operations

Use when the user asks to inspect, export, attach, pause, disable, or close the daily X followings digest cron job.

## Known daily cron job identity

As of 2026-07-05, the daily 07:00 X digest job was:

- Name: `X每日关注流日报`
- Job ID: `035d7bf27b79`
- Schedule: `0 7 * * *`
- Delivery: `origin`
- Skill: `ai-ggbond-x-followings-feed`

Do not assume this ID forever. Always list cron jobs first and match by name/schedule before acting.

## Export prompt/structure as an attachment

When the user asks for the cronjob content form, structure, or prompt as an attachment:

1. Run `cronjob(action="list")` and identify `X每日关注流日报`.
2. If full prompt is not exposed by list output, recover it from cron output/session files if available; otherwise export the visible configuration plus the known structure from the skill prompt templates.
3. Write a Markdown attachment under the current workspace, e.g. `/Users/admin/.hermes/workspaces/touyan/x_daily_cronjob_structure_<job_id>.md`.
4. Include:
   - job name, ID, schedule, delivery, enabled/state, last/next run
   - prompt主体 / execution flow
   - output section structure
   - Feishu formatting constraints: no Markdown tables, use Markdown links
   - content positioning: not news copying, but AI opportunity radar
5. Reply with `MEDIA:/absolute/path/to/file` so Feishu uploads it as an attachment.

## Pause/disable operation

When the user says “关闭/暂停/disable/stop this daily X push task”:

1. Run `cronjob(action="list")` first. Never guess the job ID.
2. Confirm the target is the daily X digest (`X每日关注流日报`, schedule `0 7 * * *`).
3. Use `cronjob(action="pause", job_id="...")` rather than remove, unless the user explicitly asks to delete permanently.
4. Final response should be terse and operational:
   - task name
   - job ID
   - original schedule
   - current state `paused / enabled=false`

Rationale: pausing preserves the prompt, skill binding, and delivery configuration for later resume. Deleting destroys useful setup state.
