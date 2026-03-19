import {
  Injectable,
  NotFoundException,
  ForbiddenException,
} from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { CreateDecisionDto, UpdateDecisionDto } from './dto/decision.dto';

@Injectable()
export class DecisionsService {
  constructor(private readonly prisma: PrismaService) {}

  async create(dto: CreateDecisionDto, userId: string) {
    const decision = await this.prisma.decision.create({
      data: {
        title: dto.title,
        contextPrompt: dto.contextPrompt,
        deadline: dto.deadline ? new Date(dto.deadline) : undefined,
        creatorId: userId,
        participants: {
          create: {
            userId,
            role: 'owner',
          },
        },
      },
      include: {
        participants: {
          include: { user: { select: { id: true, name: true, email: true } } },
        },
      },
    });

    // Write audit log
    await this.prisma.auditLog.create({
      data: {
        entityId: decision.id,
        actorId: userId,
        action: 'DECISION_CREATED',
        metadata: { title: decision.title },
      },
    });

    return decision;
  }

  async findAll(userId: string) {
    return this.prisma.decision.findMany({
      where: {
        participants: {
          some: { userId },
        },
      },
      include: {
        _count: {
          select: { participants: true },
        },
      },
      orderBy: { createdAt: 'desc' },
    });
  }

  async findOne(id: string, userId: string) {
    const decision = await this.prisma.decision.findUnique({
      where: { id },
      include: {
        participants: {
          include: {
            user: {
              select: { id: true, name: true, email: true },
            },
          },
        },
      },
    });

    if (!decision) {
      throw new NotFoundException('Decision not found');
    }

    const isParticipant = decision.participants.some(
      (p) => p.userId === userId,
    );

    if (!isParticipant) {
      throw new ForbiddenException(
        'You are not a participant of this decision',
      );
    }

    return decision;
  }

  async update(id: string, dto: UpdateDecisionDto, userId: string) {
    const decision = await this.prisma.decision.findUnique({
      where: { id },
      include: { participants: true },
    });

    if (!decision) {
      throw new NotFoundException('Decision not found');
    }

    const participant = decision.participants.find((p) => p.userId === userId);

    if (!participant || participant.role !== 'owner') {
      throw new ForbiddenException('Only the owner can update this decision');
    }

    if (decision.status !== 'DRAFT') {
      throw new ForbiddenException(
        'Decision can only be updated in DRAFT status',
      );
    }

    const updated = await this.prisma.decision.update({
      where: { id },
      data: {
        title: dto.title,
        contextPrompt: dto.contextPrompt,
        deadline: dto.deadline ? new Date(dto.deadline) : undefined,
      },
      include: {
        participants: {
          include: {
            user: {
              select: { id: true, name: true, email: true },
            },
          },
        },
      },
    });

    // Write audit log
    await this.prisma.auditLog.create({
      data: {
        entityId: id,
        actorId: userId,
        action: 'DECISION_UPDATED',
        metadata: { changes: JSON.parse(JSON.stringify(dto)) },
      },
    });

    return updated;
  }
}
