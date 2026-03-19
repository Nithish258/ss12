import { IsEmail, IsEnum } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

export enum ParticipantRoleEnum {
  owner = 'owner',
  contributor = 'contributor',
  observer = 'observer',
}

export class InviteParticipantDto {
  @ApiProperty({ example: 'jane@example.com' })
  @IsEmail()
  email: string;

  @ApiProperty({ enum: ParticipantRoleEnum, example: 'contributor' })
  @IsEnum(ParticipantRoleEnum)
  role: ParticipantRoleEnum;
}
