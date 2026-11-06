## What and why
<!-- One or two sentences. Link the issue or task. -->

## Review checklist (book Chapter 27 · Appendix E)
- [ ] Every changed file is explained by the task; no unrelated edits
- [ ] Acceptance criteria met, including empty, invalid, duplicate and "not yours" cases
- [ ] Every query on user data filters by owner; queries parameterised
- [ ] No secrets in code; input validated on the backend; nothing sensitive logged
- [ ] Errors handled, never swallowed
- [ ] New dependencies are real, maintained and needed
- [ ] New settings are in `.env.example`
- [ ] Tests added and `make test` passes
- [ ] Docs, `AGENTS.md` and diagrams updated if behaviour changed

**Working solo?** Review your own diff after a break, and ask a fresh AI session to review it against this list.
