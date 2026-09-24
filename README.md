# Diataxis skill

An agent skill that teaches Claude Code, Codex, and any other tool following the Agent Skills spec to write, review, and structure documentation with the [Diataxis framework](https://diataxis.fr). Documentation is split into four types, each serving one reader need: tutorials, how-to guides, reference, and explanation.

`SKILL.md` is the entry point. `reference/` holds the full text of diataxis.fr converted to Markdown.

## Install

Claude Code:

```
git clone https://github.com/travcunn/diataxis-skill ~/.claude/skills/diataxis
```

Codex:

```
git clone https://github.com/travcunn/diataxis-skill ~/.codex/skills/diataxis
```

To share one checkout between both, clone into `~/.agents/skills/diataxis` and symlink it from each of the directories above.

## Use

Nothing to invoke. The agent loads the skill on its own when a task involves writing, restructuring, or reviewing documentation. Mention Diataxis by name to force it. `SKILL.md` describes the four modes: classify, write one document, review, and restructure a docs set.

## Refresh the reference text

```
bash update.sh
```

The script shallow-clones the upstream repository and regenerates every page in `reference/`. It needs `python3` and `pandoc` at `/opt/homebrew/bin/pandoc`.

## License and attribution

The Diataxis text in `reference/` is by Daniele Procida and is licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). It was converted from the [diataxis-documentation-framework](https://github.com/evildmp/diataxis-documentation-framework) repository. `SKILL.md` adapts that text and carries the same license, as do the conversion scripts in this repository.
