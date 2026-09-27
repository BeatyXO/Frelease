# Frelease reviewer target

A live deployment and positive lifecycle are recorded in `deployments/studionet.json`. The following remaining proofs are not claimed as complete:

1. Confirm the live `get_config()` evaluator/owner readback.
2. Verify deployed-source parity for the Evaluator, and record verified schema hashes if exposed.
3. Activate a newer sequence, then finalize a compatible older candidate and read back `STALE_OR_NON_MONOTONIC_SEQUENCE` without head rollback.
4. Assess a duplicate-artifact candidate to a compatible verdict, then read back `ARTIFACT_ALREADY_ACTIVATED`. The recorded replay attempt was `INCONCLUSIVE` and is not sufficient.
5. Deploy/configure the frontend against the canonical addresses; test the routes, finalized checkpoint, wallet reload persistence, copy/disconnect, wrong-network switch and responsive layout.

The positive lifecycle already has a finalized parent and child plus `ACTIVATED` checkpoint/head readback. Do not describe `ACCEPTED`, `INCONCLUSIVE`, or another provisional evaluator state as an activated release.
