# Frelease reviewer target

A strong live review should demonstrate these facts from canonical state and transaction receipts:

1. Deploy `FreleaseRegistry`, deploy `FreleaseEvaluator(registry)`, finalize `set_evaluator_once`.
2. Register a policy with at least three evidence kinds and preferably two independent public origins.
3. Register candidate sequence N with a real source commit and artifact SHA-256.
4. Assess it with public evidence and show evidence-window receipts + aggregate snapshot digest.
5. Show the parent assessment reaching `FINALIZED`.
6. Recover the registry child transaction and show it reaches `FINALIZED`.
7. Read the registry checkpoint and policy head proving activation.
8. Register/assess a newer candidate N+1 and activate it.
9. Demonstrate a late older candidate cannot roll the head backward (`STALE_OR_NON_MONOTONIC_SEQUENCE`).
10. Demonstrate either artifact replay blocking or retirement-safe blocking as an additional negative path.
11. Verify deployed-source parity for both contracts and record source/schema hashes.
12. Run the production frontend against those canonical addresses and confirm wallet reload persistence, copy-address and disconnect behavior.

Do not claim a live proof until both parent and child transactions are final and canonical reads match the documentation.
