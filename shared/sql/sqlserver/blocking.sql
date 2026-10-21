-- Session A (leave transaction open for no more than 60 seconds):
USE SupportLab;
BEGIN TRAN;
UPDATE dbo.Players SET points=points+1 WHERE id=1;
-- Stop here. Run Session B below in ANOTHER connection, then observe from a third.
-- Session B:
-- USE SupportLab;
-- SET LOCK_TIMEOUT 15000;
-- BEGIN TRAN;
-- UPDATE dbo.Players SET points=points+1 WHERE id=1;
-- Session C: run diagnostics.sql while B waits.
-- A: ROLLBACK; then B: ROLLBACK; -- cleanup BOTH sessions, even after a timeout.
