---
name: diataxis
description: Use when writing or restructuring documentation of any kind, including README files, docs sites, tutorials, getting-started or quickstart pages, how-to guides, runbooks, CLI or API reference, or architecture and design explanations. Also use when reviewing or auditing existing docs, deciding what kind of document something is or where content belongs, or when docs are described as confusing or as mixing concepts with instructions. Applies whenever Diataxis is mentioned by name.
---

# Diataxis

## Overview

Diataxis classifies documentation along two axes: action versus cognition (what the reader does versus what the reader knows), and acquisition versus application (studying a skill versus applying it at work). Crossing the axes produces four types: tutorial (action, acquisition), how-to guide (action, application), reference (cognition, application), and explanation (cognition, acquisition). Each document serves exactly one of these needs, so documentation is structured by the reader's need rather than by topic or product feature.

```
              ACQUISITION (study)     APPLICATION (work)
           +------------------------+------------------------+
  ACTION   |       TUTORIAL         |      HOW-TO GUIDE       |
 (doing)   |   learning-oriented    |     goal-oriented       |
           +------------------------+------------------------+
COGNITION  |      EXPLANATION       |       REFERENCE         |
(knowing)  | understanding-oriented |   information-oriented  |
           +------------------------+------------------------+
```

Adapted from diataxis.fr by Daniele Procida, CC BY-SA 4.0. Full text in `reference/`.

## When to use this skill

Use for:
- Writing or restructuring documentation of any kind: READMEs, docs sites, tutorials, quickstarts, how-to guides, runbooks, CLI or API reference, design explanations.
- Reviewing or auditing existing docs.
- Deciding what kind of document something is, or where content belongs.
- A complaint that docs are confusing or mix concepts with instructions.
- Any mention of Diataxis by name.

Not for:
- Marketing copy.
- Changelogs.
- Commit messages.
- Inline code comments.
- Chat answers.

## How to use this skill

Four modes, matched to the request.

### Classify
Before writing anything, or when asked what kind of document something is.
1. Load [compass.md](reference/compass.md).
2. Apply the compass questions to each section or paragraph, not just the whole page: action or cognition, acquisition or application. Most pages mix several types.
3. If two adjacent types are hard to tell apart, load [tutorials-how-to.md](reference/tutorials-how-to.md) (tutorial versus how-to guide) or [reference-explanation.md](reference/reference-explanation.md) (reference versus explanation).

### Write one document
1. Classify the request first.
2. Load that type's page: [tutorials.md](reference/tutorials.md), [how-to-guides.md](reference/how-to-guides.md), [reference.md](reference/reference.md), or [explanation.md](reference/explanation.md).
3. Follow that page's structure and language rules. The Quick reference table below states the contract.

### Review or audit existing docs
Type-mixing is the root defect, so it is reported first.
1. Label every section by type, not just the page as a whole.
2. Report sections that mix types, or a page whose type does not match its title, as the primary findings.
3. Check each section against its own type's rules, from that type's page and [quality.md](reference/quality.md).
4. Only then check facts, completeness, and style.

Load [quality.md](reference/quality.md) plus whichever type pages the content touches.

### Structure or restructure a docs set
1. Treat the four types as the top level, with topic as a second level inside each.
2. Work from the existing pages rather than designing a complete architecture up front.
3. Apply the iterative method from [how-to-use-diataxis.md](reference/how-to-use-diataxis.md): pick any page, classify it, make one improvement, publish it, repeat.
4. For large or multi-product docs, also load [application.md](reference/application.md).

Load [map.md](reference/map.md) and [how-to-use-diataxis.md](reference/how-to-use-diataxis.md).

## Quick reference: the four types

| Type | Serves | Reader's question | It is | Must | Must not | Load |
|---|---|---|---|---|---|---|
| Tutorial | Acquisition, study | "Can you teach me to...?" | A lesson, a learning experience | State a concrete outcome up front. The learner does every step, each step shows a visible result, and the lesson is repeatable. | Explain concepts (link to explanation instead). Offer choices or alternatives. | [tutorials.md](reference/tutorials.md) |
| How-to guide | Application, work | "How do I...?" | A set of directions, a recipe | Address a specific real-world goal, from the user's perspective, not the machinery's. Give a logical sequence with flow, adaptable to real-world complexity. Assume the user is already competent. | Explain. Teach. List every option (link to reference instead). | [how-to-guides.md](reference/how-to-guides.md) |
| Reference | Application, work | "What is...?" | Austere description, structured like the product | Describe neutrally, accurately, and completely. Mirror the machinery's structure. Use consistent patterns. Include illustrative examples. | Explain. Instruct beyond bare usage. Offer opinion. | [reference.md](reference/reference.md) |
| Explanation | Acquisition, study | "Can you tell me about...?" | Discursive, reflective discussion of a topic | Provide context and background. Discuss alternatives, reasons, and the bigger picture. Stay bounded to one topic. | Instruct. Be required reading before the reader can act. | [explanation.md](reference/explanation.md) |

## Common mistakes

| Mistake | Fix |
|---|---|
| Docs organized by product area, with only one type split out | Restructure the top level around the four types, with topic as a second level inside each. |
| A getting-started page lists commands with no stated outcome and nothing built | Rewrite as a tutorial with one concrete goal the learner achieves, and a visible result at every step. |
| Explanation, such as "why this design", embedded in a reference page | Move it to an explanation page. Leave at most one link-out sentence behind. |
| How-to procedures, such as "retrying an operation", embedded in a reference page | Move the procedure to its own how-to guide. Reference states facts only. |
| A review ranks type-mixing as a minor style note, after factual nitpicks | Report type-mixing first. It is the root defect the other findings follow from. |
| A getting-started or tutorial page opens with a design-philosophy paragraph | A tutorial must not explain. Move the paragraph to an explanation page and link to it from the tutorial. |
| A tutorial teaches by explaining a concept instead of having the learner do something | Replace the exposition with a step the learner performs and a result they observe. |
| A reference page justifies or opines on a design choice | Move the justification to explanation. Reference only describes. |

## Reference files

| File | Covers | Load when |
|---|---|---|
| [index.md](reference/index.md) | Diataxis overview and site contents | First orientation |
| [start-here.md](reference/start-here.md) | Five-minute primer on all four types, the map, and the compass | A quick refresher |
| [compass.md](reference/compass.md) | The two classifying questions | Classifying any section or page |
| [map.md](reference/map.md) | The two-dimensional structure, why topic-based structure fails, and how types blur | Structuring a docs set |
| [tutorials.md](reference/tutorials.md) | Tutorial rules and language | Writing or reviewing a tutorial |
| [how-to-guides.md](reference/how-to-guides.md) | How-to guide rules and language | Writing or reviewing a how-to guide |
| [reference.md](reference/reference.md) | Reference rules and language | Writing or reviewing reference |
| [explanation.md](reference/explanation.md) | Explanation rules and language | Writing or reviewing explanation |
| [tutorials-how-to.md](reference/tutorials-how-to.md) | Tutorial versus how-to guide, in depth | The distinction is unclear |
| [reference-explanation.md](reference/reference-explanation.md) | Reference versus explanation, in depth | The distinction is unclear |
| [quality.md](reference/quality.md) | Functional versus deep quality, and what Diataxis can and cannot fix | Reviewing or auditing existing docs |
| [how-to-use-diataxis.md](reference/how-to-use-diataxis.md) | The iterative workflow of choosing, assessing, deciding, and doing | Restructuring a docs set |
| [application.md](reference/application.md) | Index into the four type pages plus the workflow tools | Orienting in a large or multi-product docs set |
| [foundations.md](reference/foundations.md) | Why exactly four types exist | Justifying the framework or explaining its origin |
| [theory.md](reference/theory.md) | Index into the theoretical section | Deeper theoretical grounding is needed |
| [colophon.md](reference/colophon.md) | Authorship, license, and citation | Citing or crediting Diataxis |
| [SOURCES.md](reference/SOURCES.md) | Provenance of the converted corpus and upstream URLs | Checking a source or refreshing the corpus |

Run `bash update.sh` to refresh the corpus from diataxis.fr.
