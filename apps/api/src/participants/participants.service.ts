import {
  Injectable,
  NotFoundException,
  ForbiddenException,
  ConflictException,
} from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { InviteParticipantDto } from './dto/participant.dto';

@Injectable()
export class ParticipantsService {
  constructor(private readonly prisma: PrismaService) {}

  async invite(decisionId: string, dto: InviteParticipantDto, actorId: string) {
    // Check decision exists and actor is owner
    const decision = await this.prisma.decision.findUnique({
      where: { id: decisionId },
      include: { participants: true },
    });

    if (!decision) {
      throw new NotFoundException('Decision not found');
    }

    const actorParticipant = decision.participants.find(
      (p) => p.userId === actorId,
    );

    if (!actorParticipant || actorParticipant.role !== 'owner') {
      throw new ForbiddenException('Only the owner can invite participants');
    }

    // Find user by email
    const invitedUser = await this.prisma.user.findUnique({
      where: { email: dto.email },
    });

    if (!invitedUser) {
      throw new NotFoundException('User not found with this email');
    }

    // Check if already a participant
    const existing = decision.participants.find(
      (p) => p.userId === invitedUser.id,
    );

    if (existing) {
      throw new ConflictException('User is already a participant');
    }

    // Create participant
    await this.prisma.participant.create({
      data: {
        decisionId,
        userId: invitedUser.id,
        role: dto.role,
      },
    });

    // Write audit log
    await this.prisma.auditLog.create({
      data: {
        entityId: decisionId,
        actorId,
        action: 'PARTICIPANT_INVITED',
        metadata: { invitedEmail: dto.email },
      },
    });

    // Return updated participants list
    return this.prisma.participant.findMany({
      where: { decisionId },
      include: {
        user: {
          select: { id: true, name: true, email: true },
        },
      },
    });
  }

  async remove(decisionId: string, targetUserId: string, actorId: string) {
    // Check decision exists and actor is owner
    const decision = await this.prisma.decision.findUnique({
      where: { id: decisionId },
      include: { participants: true },
    });

    if (!decision) {
      throw new NotFoundException('Decision not found');
    }

    const actorParticipant = decision.participants.find(
      (p) => p.userId === actorId,
    );

    if (!actorParticipant || actorParticipant.role !== 'owner') {
      throw new ForbiddenException('Only the owner can remove participants');
    }

    // Cannot remove yourself (the owner)
    if (targetUserId === actorId) {
      throw new ForbiddenException('Cannot remove yourself as the owner');
    }

    // Check target is a participant
    const targetParticipant = decision.participants.find(
      (p) => p.userId === targetUserId,
    );

    if (!targetParticipant) {
      throw new NotFoundException('Participant not found');
    }

    // Delete participant
    await this.prisma.participant.delete({
      where: {
        decisionId_userId: {
          decisionId,
          userId: targetUserId,
        },
      },
    });

    // Write audit log
    await this.prisma.auditLog.create({
      data: {
        entityId: decisionId,
        actorId,
        action: 'PARTICIPANT_REMOVED',
        metadata: { removedUserId: targetUserId },
      },
    });

    // Return updated participants list
    return this.prisma.participant.findMany({
      where: { decisionId },
      include: {
        user: {
          select: { id: true, name: true, email: true },
        },
      },
    });
  }
}
