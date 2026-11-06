# ADR 002: Modular monolith with layers
Date: 2026-11-05 · Status: Accepted

**Context.** One builder, under 20 requests/second, features that touch UI, API and data together.
**Options.** Monolith; modular monolith; microservices.
**Decision.** One deployable backend with modules (auth, tasks, labels, notifications), each layered
routes → services → repositories. One process also serves the built frontend.
**Consequences.** Simple to build, test, deploy and debug; boundaries kept by convention and review.
**Revisit if.** One module needs very different scaling, or several teams work independently.
