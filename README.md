# agent-skills-claude

Skills for [Claude Code](https://claude.com/claude-code).

A skill is a packaged set of instructions Claude loads when a task matches its description — a workflow, a house style, a checklist. This repo holds skills that are substantial enough to need their own reference files and research process.

## Contents

```
skills/
├── LICENSE
├── README.md                          ← you are here
├── .gitignore                         Excludes traveler-profile.md (personal data)
└── travel-agent/                      Full-service travel planning
    ├── README.md                      Full docs: install, requirements, usage
    ├── SKILL.md                        Entry point — intake, dispatch, model policy
    ├── traveler-profile.md            Your stored preferences (gitignored, local only)
    └── references/
        ├── research-rules.md          The standard all research is held to
        ├── source-map.md              Where to look, what blocks, which APIs to use
        ├── agent-briefs.md            Per-track briefs for the research agents
        ├── matrices.md                Exact column specs for every comparison table
        ├── deliverable.md             Canonical section set, report structure, publishing rules
        └── profile-template.md        Schema for traveler-profile.md
```

## What's here

**[`travel-agent/`](travel-agent/)** — plans a trip the way a good human agent does: researches everything live from operators and from people who have actually been there, then lays the options side by side as a decision document rather than a brochure. Twelve research tracks covering flights, ground transport, lodging, experiences, food, community sentiment, day trips, entry and health, points, law and stability, fare rules, and language. Output is a published, navigable artifact with a day-by-day itinerary and a booking checklist ordered by deadline.

> **Requires two agents** from [agents-claude](https://github.com/wrobelsec/agents-claude) — `travel-researcher` and `travel-scout`. The skill dispatches them by name for every research track and will not work without them. See [`travel-agent/README.md`](travel-agent/README.md).

## Install

```bash
git clone https://github.com/wrobelsec/agent-skills-claude.git ~/.claude/skills
```

Or copy a single skill into an existing setup:

```bash
cp -r travel-agent ~/.claude/skills/
```

Then install the required agents:

```bash
git clone https://github.com/wrobelsec/agents-claude.git ~/.claude/agents
```

## Related

- **[agents-claude](https://github.com/wrobelsec/agents-claude)** — the subagent definitions these skills dispatch.

## Licence

See [LICENSE](LICENSE).
