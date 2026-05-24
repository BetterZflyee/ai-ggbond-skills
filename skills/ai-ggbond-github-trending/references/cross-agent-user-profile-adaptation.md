# Cross-Agent User Profile Adaptation for GitHub Trending Analysis

Session learning: a GitHub Trending skill should not hardcode one user's identity. The skill should define the work method, while the active agent/user profile defines the analysis lens.

## Principle

- Skill = how to analyze GitHub Trending.
- User profile / memory = for whom the analysis is optimized.
- Project context = where the work is happening and what constraints apply.

A portable skill should behave like:

```python
def analyze_trending(repo_list, user_profile, project_context):
    ...
```

not:

```python
def analyze_trending_for_one_person(repo_list):
    ...
```

## Candidate Profile Sources by Agent

### Hermes Agent

- User profile: `~/.hermes/memories/USER.md`
- Work/environment memory: `~/.hermes/memories/MEMORY.md`
- Installed skills: `$HERMES_HOME/skills/`
- Project context may include `AGENTS.md`, `CLAUDE.md`, or repo docs.

### Claude Code

- Global user/project memory: `~/.claude/CLAUDE.md`
- Project context: `./CLAUDE.md`
- Local personal project override: `./.claude/CLAUDE.local.md`
- Modular rules: `~/.claude/rules/*.md`, `./.claude/rules/*.md`

### OpenCode

- Global rules/profile: `~/.config/opencode/AGENTS.md`
- Project rules: `./AGENTS.md`
- Fallbacks may include `~/.claude/CLAUDE.md` and `./CLAUDE.md` if no `AGENTS.md` exists.
- Custom instruction files can be configured in `opencode.json` / `~/.config/opencode/opencode.json`.

### Codex

- Project and nested context: `AGENTS.md`
- Some environments may have global/custom instructions injected by launcher or config.
- Treat `AGENTS.md` as project/task rules unless it explicitly contains user-level preferences.

### OpenClaw / Other Agents

- Prefer standards first: `AGENTS.md`, `CLAUDE.md`, tool-specific config.
- If profile source is unknown, do not invent one. Use current conversation context and ask when personalization materially matters.

## Recommended Priority

When multiple profile/context files exist, avoid blindly merging everything. Use this hierarchy:

1. Current conversation/system-injected user profile, if available.
2. Active agent's native user-profile memory.
3. Project-level context files for current working directory.
4. Compatible fallback files (`AGENTS.md`, `CLAUDE.md`).
5. Generic analysis framework if no user profile is available.

User-level profile answers: “What does this user care about?”
Project-level context answers: “What constraints and conventions apply here?”
Skill answers: “What procedure should be followed?”

## Clarifying Questions Before Implementing Cross-Agent Detection

If the user asks to upgrade the skill to auto-detect user profile sources, ask before editing:

1. Should detection be documented only in `SKILL.md`, implemented in script, or both?
2. Which agents are first-version scope: Hermes, Claude Code, Codex, OpenCode, OpenClaw, CodeDesk, others?
3. Should the skill read profile file contents, only detect paths, or rely on already-injected context?
4. If multiple profiles exist, what priority should be used?
5. Should there be a private user-specific mode and a generic public mode?
6. Should the final report show the detected profile source / adaptation lens?
7. What default framework should apply when no profile is found?

## Generic Default Analysis Lenses

If no user profile is available, classify projects by:

- Developer value: productivity, learning, reusable tooling.
- Product value: product pattern, UX, workflow shift.
- Business value: commercialization potential, enterprise adoption.
- Content value: narrative strength, explainability, audience fit.
- Network value: worth following authors/community or contributing.

## Pitfall

Do not write personal names, goals, or private strategy directly into a portable/public skill unless it is intentionally a private skill. Prefer a `User Profile Adaptation` section that says to adapt to the active user's profile.
