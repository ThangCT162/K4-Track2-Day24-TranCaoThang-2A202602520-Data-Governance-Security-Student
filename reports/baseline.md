# Baseline review

1. `_naive_loop()` has no per-run principal or identity binding; it trusts the model's customer IDs.
2. No policy check authorizes `read_customer` or `http_post` before execution.
3. `reports/attack-before.log` proves the baseline sent the synthetic `KH-000999` record, including CCCD, phone and bank account, to the localhost sink.
