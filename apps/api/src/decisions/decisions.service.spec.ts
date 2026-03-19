import { Test, TestingModule } from '@nestjs/testing';
import { DecisionsService } from './decisions.service';
import { PrismaService } from '../prisma/prisma.service';
import { ForbiddenException, NotFoundException } from '@nestjs/common';

const mockPrisma = {
  decision: {
    create: jest.fn(),
    findMany: jest.fn(),
    findUnique: jest.fn(),
    update: jest.fn(),
  },
  auditLog: { create: jest.fn() },
};

describe('DecisionsService', () => {
  let service: DecisionsService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        DecisionsService,
        { provide: PrismaService, useValue: mockPrisma },
      ],
    }).compile();
    service = module.get<DecisionsService>(DecisionsService);
    jest.clearAllMocks();
  });

  it('should create decision and add owner participant', async () => {
    const mockDecision = {
      id: 'd1', title: 'Test', status: 'DRAFT',
      participants: [{ userId: 'u1', role: 'owner', user: {} }],
    };
    mockPrisma.decision.create.mockResolvedValue(mockDecision);
    mockPrisma.auditLog.create.mockResolvedValue({});
    const result = await service.create({ title: 'Test' }, 'u1');
    expect(result.id).toBe('d1');
    expect(mockPrisma.decision.create).toHaveBeenCalledTimes(1);
  });

  it('should throw NotFoundException for unknown decision', async () => {
    mockPrisma.decision.findUnique.mockResolvedValue(null);
    await expect(service.findOne('bad-id', 'u1')).rejects.toThrow(NotFoundException);
  });

  it('should throw ForbiddenException if not a participant', async () => {
    mockPrisma.decision.findUnique.mockResolvedValue({
      id: 'd1', participants: [{ userId: 'other-user' }],
    });
    await expect(service.findOne('d1', 'u1')).rejects.toThrow(ForbiddenException);
  });

  it('should throw ForbiddenException on PATCH if not DRAFT', async () => {
    mockPrisma.decision.findUnique.mockResolvedValue({
      id: 'd1', status: 'SUBMISSION_OPEN',
      participants: [{ userId: 'u1', role: 'owner' }],
    });
    await expect(
      service.update('d1', { title: 'New' }, 'u1')
    ).rejects.toThrow(ForbiddenException);
  });
});
