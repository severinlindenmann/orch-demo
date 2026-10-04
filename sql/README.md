# sql/

Plain SQL models with Jinja-style `{{ source(...) }}` / `{{ ref(...) }}`
placeholders, run today by a thin in-house runner (not dbt).

## dbt vs. plain SQL (spike notes, DEMO-0008)

We looked at adopting dbt-core for `staging/` and `marts/`. Draft
findings:

- dbt would buy us `ref()`/`source()` resolution, docs generation and
  `dbt test` for free, instead of our hand-rolled runner.
- Migration cost for the 4 existing models is small, but we'd also
  need to stand up a `profiles.yml` per environment and CI changes.
- Decision: **not now.** Revisit once we have more than ~10 models;
  today the overhead isn't worth it for 4 files.

See issue #2 for the full discussion.
