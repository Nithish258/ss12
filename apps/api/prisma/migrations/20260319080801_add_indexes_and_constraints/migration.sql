/*
  Warnings:

  - A unique constraint covering the columns `[decisionId,userId]` on the table `Submission` will be added. If there are existing duplicate values, this will fail.

*/
-- CreateIndex
CREATE INDEX "AuditLog_entityId_idx" ON "AuditLog"("entityId");

-- CreateIndex
CREATE INDEX "AuditLog_actorId_idx" ON "AuditLog"("actorId");

-- CreateIndex
CREATE INDEX "AuditLog_timestamp_idx" ON "AuditLog"("timestamp");

-- CreateIndex
CREATE INDEX "Decision_creatorId_idx" ON "Decision"("creatorId");

-- CreateIndex
CREATE INDEX "Decision_status_idx" ON "Decision"("status");

-- CreateIndex
CREATE INDEX "Participant_userId_idx" ON "Participant"("userId");

-- CreateIndex
CREATE INDEX "Submission_decisionId_idx" ON "Submission"("decisionId");

-- CreateIndex
CREATE INDEX "Submission_userId_idx" ON "Submission"("userId");

-- CreateIndex
CREATE UNIQUE INDEX "Submission_decisionId_userId_key" ON "Submission"("decisionId", "userId");
