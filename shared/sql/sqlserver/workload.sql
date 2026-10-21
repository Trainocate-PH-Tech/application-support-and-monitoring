USE SupportLab;
SET STATISTICS IO ON;
SET STATISTICS TIME ON;
DECLARE @n int=0;
WHILE @n<30 BEGIN
 SELECT SUM(amount) FROM dbo.Transactions WHERE player_id=42;
 SET @n+=1;
END;
-- Instructor: compare plan/logical reads before and after this approved lab change:
-- CREATE INDEX IX_Transactions_Player ON dbo.Transactions(player_id) INCLUDE(amount);
-- Reset: DROP INDEX IF EXISTS IX_Transactions_Player ON dbo.Transactions;
-- Do not equate elapsed time to CPU or force plans from one observation.
