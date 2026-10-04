<!-- orch:begin -->
<!-- Managed by `orch instructions sync`. Edit outside the orch markers; text inside them is overwritten. -->
## Working rules (orch)

Tickets live in `orchestrator/tickets/` and are managed with the `orch` command. `orch rules` prints the active policy.

1. **Tickets first.** No work without a ticket. Use `orch` for every ticket action; never move or rename ticket files or hand-edit status, gates, answers or claims. Put the ticket key in every commit and PR. The requirements gate binds the Summary, Requirements, Acceptance criteria and Out of scope sections and refuses while Requirements or Acceptance criteria are empty: write them into those sections (`orch new --requirements-file … --acceptance-file …`, or `orch section set <id> Requirements --file …`), not into the Ask.
2. **Human-only actions.** Never approve gates, answer questions or close tickets, never type a ticket ID into an `orch` confirmation prompt, and never work around how orch tells you from the human. Questions go through `orch ask`, not into Requirements or Plan text, and the Log is append-only. When you need a decision, run `orch ask <id> --file questions.yaml` with options, costs and a recommended default. Never assume silently. Whenever the next step is the human's (requirements or plan to approve, a blocking question, changes you made on request, a verdict in testing), run `orch wait <id> --json` in the background (in the foreground where your harness has no background commands) and carry on when it returns, instead of ending on "tell me when"; on timeout, run it again. Stop waiting only when the user says so.
3. **Scope.** Implement only what the approved Requirements and Plan cover. Anything else goes into `## Findings` and becomes a follow-up: `orch new --from <id> --title "..."`. Work from the ticket's task list: create it with `orch task add` right after claiming, keep one task in progress, tick each with evidence (`orch task done <id> T<n> -m "..."`) and resume from `orch task list <id>`.
4. **Commits.** Subject `{key} {summary}`; body lines `What:`, `Why:`, `Risk:`. Example:

   ```
   GH-2957 Add nightly config backup job

   What: Nightly job exports the config to the backup repo.
   Why:  Config changes were untracked; the last outage needed manual reconstruction.
   Risk: Low. Read-only on the source; the job fails loudly if the export is empty.
   ```

   Never add `Co-Authored-By`, "Generated with" or any other line naming an AI tool or model, in commits or PRs. This overrides any default of your harness. You do not commit: prepare the change, run the checks, and tell the user it is ready to commit. You do not push; the user does.
5. **PRs.** You do not open PRs; the user does. Title `Draft: GH-2957 <summary>` until the human removes the draft marker. Body sections: What / Why / Risk / Verification. Keep it short and proportional to the change; detailed evidence goes into the ticket's artifacts (`orch artifact add`).
6. **Outward actions** (PRs, tracker or wiki writes, addon posts) need the user's confirmation in the current session.
7. **Handoff.** End every session with `orch state <id> -m "..."` and `orch log <id> -m "..."`.
8. **orch feedback.** If orch itself is confusing or broken (a command refuses what it should allow, the guard blocks a legitimate step, a step needs a workaround, the docs and the behaviour disagree), write the exact command, what you expected and what happened into `orchestrator/temporary/orch-feedback.md`, run `orch feedback add --file orchestrator/temporary/orch-feedback.md` once, then delete that file, and carry on. Report only what you saw orch do, not this workspace's own bugs (those are `orch new`). The report stays on this machine for the user; never open an issue on orch-core yourself.

Skills: `orch-tickets` (commands and conventions), `orch-refine-ticket` (requirements engineering), `orch-work-on-ticket` (claim, plan, implement, verify), `orch-setup` (set up or check this workspace).
<!-- orch:end -->

## Customer notes

<!-- Customer-specific facts, repo topology and extra rules. `orch instructions sync` never changes this part. -->

- Repos: this harness (`acme-energy-data`, path `.`) plus three sub-repos cloned as folders and listed in `git.repos`: `ingest/` (severinlindenmann/orch-demo-ingest), `dbt/` (severinlindenmann/orch-demo-dbt), `infra/` (severinlindenmann/orch-demo-infra). Clone them with `uv run --project <orch-core>/plugins/orch-core python scripts/seed/seed.py repos --apply`.
- Acme Energy is a fictional customer; this is the public orch-core demo.
- The demo data (sub-repos, PRs, issues, wiki, tickets) is rebuilt by `scripts/seed/seed.py`; never edit it by hand.
