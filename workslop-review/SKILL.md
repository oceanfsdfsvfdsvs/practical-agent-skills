---
name: workslop-review
description: Review AI-generated workplace drafts before they create downstream rework. Use when a user asks whether an AI-written email, report, brief, PRD, proposal, meeting summary, slide outline, analysis, or handoff is ready to send, needs repair, lacks evidence, contains hallucinated claims, or feels like "workslop".
---

# Workslop Review

## Overview

Use this skill to gate AI-generated work before it reaches another person. The goal is not to make the draft prettier; it is to decide whether it is useful, grounded, complete, and accountable enough to send.

## When to Use

- Reviewing an AI-generated workplace artifact for send/readiness.
- Turning a vague AI draft into a concrete, source-backed deliverable.
- Finding missing context, unsupported claims, unclear owners, vague next steps, or hidden assumptions.
- Producing a minimal repair plan when a draft would force the recipient to do the real work.

Do not use this skill for pure prose cleanup, code review, security review, SEO audits, or general research unless the draft's core problem is AI-generated work quality and downstream rework risk.

## Required Inputs

Ask for only the missing inputs that materially affect the decision. If the user wants a fast pass, proceed with explicit assumptions.

- Draft or artifact to review.
- Intended recipient or audience.
- Goal of the artifact.
- Available source material, context, links, notes, or data.
- Constraints such as tone, deadline, confidentiality, legal/compliance limits, or required format.

## Workflow

### 1. Classify the Artifact

Identify the artifact type, audience, decision it is supposed to enable, and the cost if it is wrong. Treat executive, customer-facing, legal, financial, medical, HR, security, and public claims as higher risk.

### 2. Build the Evidence Map

Read `references/workslop-patterns.md` when the draft is long, high stakes, or hard to judge quickly. Use `templates/review-rubric.md` when the user needs a repeatable review artifact.

Extract:

- Factual claims that need support.
- Recommendations or decisions.
- Action items, owners, due dates, and dependencies.
- Assumptions and unstated context.
- Ambiguous references such as "they", "this", "soon", "high priority", or "best".
- Missing inputs the recipient would need to finish the work.

If claims depend on current facts, external sources, numbers, prices, laws, product behavior, or named organizations, verify them with sources or mark them unverified. Never invent citations or treat polished language as evidence.

### 3. Score the Workslop Risk

Score each dimension 0-2:

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| Context fit | Missing audience/goal | Partly aligned | Clearly tailored |
| Grounding | Unsupported or likely false | Some support, gaps remain | Evidence-backed |
| Actionability | Vague or passive | Some next steps | Clear owners/actions |
| Completeness | Recipient must reconstruct | Minor gaps | Self-contained |
| Specificity | Generic AI phrasing | Mixed | Concrete and precise |
| Risk control | Sensitive or risky issues ignored | Risks noted incompletely | Risks handled |

Decision:

- 11-12: Sendable.
- 8-10: Sendable after minor edits.
- 5-7: Repair before sending.
- 0-4: Reject and rebuild from source material.

Override the numeric score to "Reject and rebuild" if the draft contains material unsupported high-stakes claims, confidential data exposure, fabricated sources, invented commitments, or instructions that could cause harm.

### 4. Repair the Minimum Necessary

Prioritize fixes that reduce downstream work:

- Add missing decision context.
- Replace vague claims with sourced, bounded claims.
- Convert broad recommendations into explicit actions.
- Separate facts, assumptions, and opinions.
- Remove filler that hides lack of substance.
- Ask for missing inputs only when they block delivery.

When rewriting, preserve the user's intent and produce the smallest useful patch. Do not silently change commitments, ownership, dates, figures, or policy claims.

## Output Format

Use this structure unless the user asks for a different format:

```markdown
## Delivery Decision
[Sendable / Minor edits / Repair first / Reject and rebuild]

## Score
| Dimension | Score | Reason |
|---|---:|---|
| Context fit | 0-2 | ... |
| Grounding | 0-2 | ... |
| Actionability | 0-2 | ... |
| Completeness | 0-2 | ... |
| Specificity | 0-2 | ... |
| Risk control | 0-2 | ... |

## Main Problems
1. [Issue, why it matters, recipient impact]
2. ...

## Minimal Repair
[Revised passage, outline, or concrete edits]

## Missing Inputs
[Only blockers or important verification gaps]

## Ready-to-Send Version
[Include only when the draft can be safely repaired in this pass]
```

## Examples

User: "Use $workslop-review on this AI-generated client update. Is it safe to send?"

Response: classify the update, score it, flag unsupported claims or vague commitments, repair the update, and provide a ready-to-send version only if the facts are sufficiently grounded.

User: "This AI-made research brief feels generic. Fix it."

Response: extract claims, verify or mark unsupported claims, identify missing decision context, then rebuild the brief around the user's audience and source material.

See `examples/bad-status-update.md` for a compact before/after example and the minimum repair style this skill should prefer.
