# DPIA-lite

## Data and purpose

The mock agent processes synthetic support tickets and synthetic customer records. The purpose is ticket summarization and a controlled support-reply workflow.

## Flow and controls

Run A searches untrusted ticket content. Run B receives only typed ticket IDs and resolves customer records through trusted `related_tickets` mappings. Policy checks principal, purpose, scopes, expiry, classification and egress before every tool call. The ledger records decisions without raw PII.

## Limits

This is a local deterministic mock. `--as` selects a fixture principal and is not production authentication. The localhost sink and hash-chain ledger are lab evidence, not a complete production DLP, identity, key-management or immutable audit service. Legal mappings require verification against authoritative source texts.
