# Claude Code ToolBox — MCP & Skills awareness

_Generated: 2026-10-25T01:50:40.095Z_

## How to use this report

- **Saved copy:** This file is **`.claude/cloude-code-toolbox-mcp-skills-awareness.md`** — refreshed whenever the toolbox runs an MCP & Skills scan (including on workspace open when auto-scan is enabled). It is meant for **Claude Code workspace context** together with `CLAUDE.md` (which gets a shorter replaceable summary when auto-merge is on).
- **MCP:** Lists **configured** servers from Claude Code config (`~/.claude.json` for user scope, `.mcp.json` for project scope). Use `/mcp` in the Claude Code panel to connect servers for your session.
- **Skills:** **On-disk** folders with `SKILL.md`. Claude Code does not auto-load them; attach `SKILL.md` or paths in chat when useful.
- **Task routing:** When the user’s request matches a server’s purpose (e.g. Confluence → Confluence/Atlassian MCP), prefer that **server id** from the tables below.

---

## MCP — workspace

Workspace `mcp.json` _(folder: Desarrollo-de-un-sistema-de-reservas-con-agentes)_

- **c:\Users\espin\OneDrive\Documentos\LISI\Topicos Avanzados De Ingenieria De Software\SDD\Desarrollo-de-un-sistema-de-reservas-con-agentes\.mcp.json** — _File missing_

_No active workspace servers in mcp.json._

## MCP — user profile

- **C:\Users\espin\.claude.json** — _File exists — servers defined_

| Server id | Kind | Detail |
|-----------|------|--------|
| context7 | stdio | npx -y --package=@upstash/context7-mcp@2.2.5 -- context7-mcp |
| engram | stdio | engram mcp --tools=agent |

## Skills (local `SKILL.md` folders)

### Project-scoped

- **reflex-rules** — `c:\Users\espin\OneDrive\Documentos\LISI\Topicos Avanzados De Ingenieria De Software\SDD\Desarrollo-de-un-sistema-de-reservas-con-agentes\.claude\skills\reflex-rules`
  - **Description:** Genera o modifica la interfaz web de un proyecto Reflex (Python) respetando la arquitectura por capas, las restricciones de Reflex 0.10 y las reglas del proyecto de reservas de laboratorio.

### User-scoped

- **chained-pr** — `C:\Users\espin\.claude\skills\chained-pr`
  - Trigger: PRs over 400 lines, stacked PRs, review slices. Split oversized changes into chained PRs that protect review focus.

- **cognitive-doc-design** — `C:\Users\espin\.claude\skills\cognitive-doc-design`
  - Design docs that reduce cognitive load. Trigger: writing guides, READMEs, RFCs, onboarding, architecture, or review-facing docs.

- **go-testing** — `C:\Users\espin\.claude\skills\go-testing`
  - Trigger: Go tests, go test coverage, Bubbletea teatest, golden files. Apply focused Go testing patterns.

- **judgment-day** — `C:\Users\espin\.claude\skills\judgment-day`
  - Trigger: judgment day, dual review, adversarial review, juzgar. Run explicit blind dual review with at most two scoped fix/re-judgment rounds.

- **skill-creator** — `C:\Users\espin\.claude\skills\skill-creator`
  - Trigger: new skills, agent instructions, documenting AI usage patterns. Create LLM-first skills with valid frontmatter.

- **skill-improver** — `C:\Users\espin\.claude\skills\skill-improver`
  - Trigger: improve skills, audit skills, refactor skills, skill quality. Audit and upgrade existing LLM-first skills.

- **skill-registry** — `C:\Users\espin\.claude\skills\skill-registry`
  - Trigger: update skills, skill registry, actualizar skills, after skill changes. Index available skills by trigger and path.

- **work-unit-commits** — `C:\Users\espin\.claude\skills\work-unit-commits`
  - Plan commits as reviewable work units. Trigger: implementation, commit splitting, chained PRs, or keeping tests and docs with code.

---

## Suggested next steps

- **MCP:** Use this extension’s hub **MCP** tab, or `claude mcp list` in the terminal. In Claude Code, use `/mcp` to connect servers for the session.
- **Edit config:** Open `~/.claude.json` (user MCP) or `<workspace>/.mcp.json` (project MCP) via the extension commands.
- **Refresh this report:** run **Intelligence — scan MCP & Skills awareness** again after changing MCP config or adding skills.

_Report from Claude Code ToolBox extension._
