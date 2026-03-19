import { Test, TestingModule } from '@nestjs/testing';
import { AuthService } from './auth.service';
import { PrismaService } from '../prisma/prisma.service';
import { JwtService } from '@nestjs/jwt';
import { ConflictException, UnauthorizedException } from '@nestjs/common';

const mockPrisma = {
  user: {
    findUnique: jest.fn(),
    create: jest.fn(),
  },
  auditLog: {
    create: jest.fn(),
  },
};

const mockJwt = {
  sign: jest.fn().mockReturnValue('mock.jwt.token'),
};

describe('AuthService', () => {
  let service: AuthService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        AuthService,
        { provide: PrismaService, useValue: mockPrisma },
        { provide: JwtService, useValue: mockJwt },
      ],
    }).compile();
    service = module.get<AuthService>(AuthService);
    jest.clearAllMocks();
  });

  describe('register', () => {
    it('should create user and return JWT', async () => {
      mockPrisma.user.findUnique.mockResolvedValue(null);
      mockPrisma.user.create.mockResolvedValue({
        id: 'uuid-1', email: 'a@b.com', name: 'A', role: 'user',
      });
      mockPrisma.auditLog.create.mockResolvedValue({});
      const result = await service.register({
        name: 'A', email: 'a@b.com', password: 'Password1',
      });
      expect(result.access_token).toBe('mock.jwt.token');
    });

    it('should throw ConflictException if email taken', async () => {
      mockPrisma.user.findUnique.mockResolvedValue({ id: 'existing' });
      await expect(
        service.register({ name: 'A', email: 'a@b.com', password: 'Password1' })
      ).rejects.toThrow(ConflictException);
    });
  });

  describe('login', () => {
    it('should throw UnauthorizedException for wrong password', async () => {
      mockPrisma.user.findUnique.mockResolvedValue({
        id: 'u1', email: 'a@b.com', role: 'user',
        passwordHash: '$2b$10$invalidhash',
      });
      await expect(
        service.login({ email: 'a@b.com', password: 'WrongPass1' })
      ).rejects.toThrow(UnauthorizedException);
    });

    it('should throw UnauthorizedException for unknown email', async () => {
      mockPrisma.user.findUnique.mockResolvedValue(null);
      await expect(
        service.login({ email: 'ghost@b.com', password: 'Password1' })
      ).rejects.toThrow(UnauthorizedException);
    });
  });
});
