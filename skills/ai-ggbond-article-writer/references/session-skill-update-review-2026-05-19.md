# Session skill update review — 2026-05-19

## Context

The user asked whether the learning from a WeChat article (`https://mp.weixin.qq.com/s/93VMIcvAt4LT5n8vyZ0BYA`) could be incorporated into their writing rules. The article summarized 朱朱侠内部分享 on content creation.

This session updated `ai-ggbond-article-writer` from v2.1.0 to v2.2.0, then this review tightened it to v2.2.1 by adding explicit review/verification lessons.

## What was learned

The useful class-level writing method is:

```text
Good content = information acquisition × angle selection × rhythmic storytelling × positive values
```

Key conversion into 飞哥's writing system:

1. **Information is not enough**
   - Avoid AI-circle-only input.
   - Treat information sources like a portfolio: AI/tech as main position; comedy, film, history, business, psychology, and daily observation as satellite positions.
   - Each deep article should include at least 2 cross-domain analogies or source categories.

2. **Angle determines survival**
   - Before drafting, produce an angle-exclusion table.
   - Exclude the first three obvious/common angles.
   - Pick an angle with contrast: `情理之中，预料之外`.
   - Use `陌生化`: make a familiar topic feel newly perceived.

3. **Creation must have rhythm, not documentation flatness**
   - Deep articles need a story arc, not just structured explanation.
   - Mark at least 3 `升番点` in the outline:
     - phenomenon → judgment
     - judgment → mechanism
     - mechanism → action/assets/business result
   - Every 800-1200 Chinese characters should contain a real cognitive upgrade, not a repeated restatement.

4. **Values are safety rails**
   - Do not fake expertise.
   - Avoid political/social-conflict/person-label-sensitive topics.
   - Keep a humble stance (`弱者思维`) even when the judgment is sharp.

5. **Post-draft operational questions**
   - Why would the reader finish?
   - Why would the reader like?
   - Why would the reader share?
   - Is this merely information, or a reproducible story/judgment?

## Skill maintenance lesson

When incorporating external writing methodology into a skill:

1. Use `web-access`/web extraction first; do not infer from URL title alone.
2. Patch the active class-level umbrella skill, not create a one-off skill.
3. Put durable methodology in `SKILL.md`.
4. Put session-specific/external-source digestion in `references/`.
5. Add a one-line pointer from `SKILL.md` to the support file.
6. Verify by checking:
   - version field updated;
   - new section exists;
   - support file exists;
   - support file is linked;
   - core terms such as `角度排除表`, `升番`, `陌生化` exist.
7. If the skill is GitHub-synced, run the existing sync workflow and verify the latest commit.

## Why v2.2.1 exists

v2.2.0 absorbed the methodology. v2.2.1 adds the meta-rule that future external methodology absorption should preserve both:

- **class-level rule** in `SKILL.md`, and
- **source-specific detail** in `references/`.

This prevents the skill from becoming a flat pile of one-session entries while still preserving the useful trace of the session.
