# Database topic evidence

All files are synthetic, not EC2 observations. Each subdirectory is a self-contained input for one reporting utility. Preserve provenance when copying. TSV headers define exact fields and units; scripts accept normalized TSV, not arbitrary database-client output.

| Directory | Case and expected results |
|---|---|
| mysql-slow | Four complete slow entries, 6.60 seconds total, 300000 examined rows; frequent report group about 3.6 seconds, rare delay 3 seconds. |
| mysql-contention | Lock wait 42 → 41, historical deadlock, and a separately labeled replica incident: unknown lag, 410-second visible-write gap, 420-second visible-write age. |
| mssql-diagnostics | Active requests, cached cost, Query Store, and one deliberately failed Agent step plus its job summary. |
| mssql-regression | Separate blocking case rooted at session 61 and deployment regression: 60 → 900 ms weighted duration, 220 → 21000 reads. No real plan XML is supplied. |
| app-db | Four requests with explicit DB-operation matches, two error responses, zero timing residuals; separate pool, SQL, and downstream cases. |

Full input contracts, manual investigations, and reporting instructions are in the root-level companion exercises. Keep header-only/unavailable data distinct from malformed input and from healthy observations.
