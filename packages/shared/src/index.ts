import { z } from 'zod';

// ─── Enums ───────────────────────────────────────────────────────────────────

export enum DecisionStatus {
  DRAFT = 'DRAFT',
  SUBMISSION_OPEN = 'SUBMISSION_OPEN',
  LOCKED_PROCESSING = 'LOCKED_PROCESSING',
  REVEAL_READY = 'REVEAL_READY',
  DISCUSSION = 'DISCUSSION',
  VOTING = 'VOTING',
  CLOSED = 'CLOSED',
}

export enum ParticipantRole {
  owner = 'owner',
  contributor = 'contributor',
  observer = 'observer',
}

// ─── Zod Schemas ─────────────────────────────────────────────────────────────

export const CreateDecisionDtoSchema = z.object({
  title: z.string().min(1),
  contextPrompt: z.string().optional(),
  deadline: z.string().optional(),
});

export type CreateDecisionDto = z.infer<typeof CreateDecisionDtoSchema>;

export const InviteParticipantDtoSchema = z.object({
  email: z.string().email(),
  role: z.nativeEnum(ParticipantRole),
});

export type InviteParticipantDto = z.infer<typeof InviteParticipantDtoSchema>;

export const UpdateDecisionDtoSchema = z.object({
  title: z.string().min(1).optional(),
  contextPrompt: z.string().optional(),
  deadline: z.string().optional(),
});

export type UpdateDecisionDto = z.infer<typeof UpdateDecisionDtoSchema>;

export const RegisterSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  email: z.string().email('Invalid email address'),
  password: z.string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$/, 
      'Must contain uppercase, lowercase, and a number'),
});

export type RegisterInput = z.infer<typeof RegisterSchema>;
