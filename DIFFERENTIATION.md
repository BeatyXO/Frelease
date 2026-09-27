# Clean-room differentiation

Frelease was designed to match a high reviewer bar without copying the product shape of scientific replication protocols.

Its domain object is a **software release candidate**, not a study or replication. Its frozen object is a compatibility policy, not a preregistration. Its semantic outcomes are compatibility states, not scientific replication outcomes. It has no research reward pool, researcher payout, study archive or scientific truth framing.

The architecture is deliberately two contracts rather than reproducing a three-contract registry/engine/pool pattern. The registry combines immutable release policy with deterministic canonical release-head state because they belong to one release-governance domain. The evaluator is isolated because semantic evidence assessment is the nondeterministic domain boundary.

Distinct Frelease mechanics include monotonic release sequencing, duplicate per-policy sequence rejection, retired-policy finalization blocking and already-activated artifact replay protection.
