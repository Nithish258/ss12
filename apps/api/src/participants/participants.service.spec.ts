import { Test, TestingModule } from '@nestjs/testing';
import { ParticipantsService } from './participants.service';
import { PrismaService } from '../prisma/prisma.service';
import { ForbiddenException, NotFoundException, ConflictException } from '@nestjs/common';
import { ParticipantRoleEnum } from './dto/participant.dto';

const mockPrisma = {
  decision: {
    findUnique: jest.fn(),
  },
  user: {
    findUnique: jest.fn(),
  },
  participant: {
    create: jest.fn(),
    delete: jest.fn(),
    findMany: jest.fn(),
  },
  auditLog: {
    create: jest.fn(),
  },
};

describe('ParticipantsService', () => {
  let service: ParticipantsService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        ParticipantsService,
        { provide: PrismaService, useValue: mockPrisma },
      ],
    }).compile();
    service = module.get<ParticipantsService>(ParticipantsService);
    jest.clearAllMocks();
  });

  describe('invite', () => {
    it('should invite a user successfully', async () => {
      mockPrisma.decision.findUnique.mockResolvedValue({
        id: 'd1',
        participants: [{ userId: 'owner-id', role: 'owner' }],
      });
      mockPrisma.user.findUnique.mockResolvedValue({
        id: 'user-id',
        email: 'test@example.com',
      });
      mockPrisma.participant.create.mockResolvedValue({});
      mockPrisma.auditLog.create.mockResolvedValue({});
      mockPrisma.participant.findMany.mockResolvedValue([
        { userId: 'owner-id', role: 'owner' },
        { userId: 'user-id', role: 'contributor' },
      ]);

      const result = await service.invite(
        'd1',
        { email: 'test@example.com', role: ParticipantRoleEnum.contributor },
        'owner-id',
      );

      expect(mockPrisma.participant.create).toHaveBeenCalled();
      expect(result).toHaveLength(2);
    });

    it('should throw ForbiddenException if actor is not the owner', async () => {
      mockPrisma.decision.findUnique.mockResolvedValue({
        id: 'd1',
        participants: [{ userId: 'actor-id', role: 'contributor' }],
      });

      await expect(
        service.invite('d1', { email: 'test@example.com', role: ParticipantRoleEnum.contributor }, 'actor-id')
      ).rejects.toThrow(ForbiddenException);
    });

    it('should throw ConflictException if user is already a participant', async () => {
      mockPrisma.decision.findUnique.mockResolvedValue({
        id: 'd1',
        participants: [
          { userId: 'owner-id', role: 'owner' },
          { userId: 'user-id', role: 'contributor' },
        ],
      });
      mockPrisma.user.findUnique.mockResolvedValue({
        id: 'user-id',
        email: 'test@example.com',
      });

      await expect(
        service.invite('d1', { email: 'test@example.com', role: ParticipantRoleEnum.observer }, 'owner-id')
      ).rejects.toThrow(ConflictException);
    });
  });

  describe('remove', () => {
    it('should remove a participant successfully', async () => {
      mockPrisma.decision.findUnique.mockResolvedValue({
        id: 'd1',
        participants: [
          { userId: 'owner-id', role: 'owner' },
          { userId: 'target-id', role: 'contributor' },
        ],
      });
      mockPrisma.participant.delete.mockResolvedValue({});
      mockPrisma.auditLog.create.mockResolvedValue({});
      mockPrisma.participant.findMany.mockResolvedValue([
        { userId: 'owner-id', role: 'owner' },
      ]);

      const result = await service.remove('d1', 'target-id', 'owner-id');
      expect(mockPrisma.participant.delete).toHaveBeenCalledWith({
        where: { decisionId_userId: { decisionId: 'd1', userId: 'target-id' } },
      });
      expect(result).toHaveLength(1);
    });

    it('should throw ForbiddenException if trying to remove self (owner)', async () => {
      mockPrisma.decision.findUnique.mockResolvedValue({
        id: 'd1',
        participants: [{ userId: 'owner-id', role: 'owner' }],
      });

      await expect(
        service.remove('d1', 'owner-id', 'owner-id')
      ).rejects.toThrow(ForbiddenException);
    });
  });
});
