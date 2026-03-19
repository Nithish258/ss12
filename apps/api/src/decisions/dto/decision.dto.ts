import { IsNotEmpty, IsOptional, IsString } from 'class-validator';
import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';

export class CreateDecisionDto {
  @ApiProperty({ example: 'Q4 Budget Allocation' })
  @IsString()
  @IsNotEmpty()
  title: string;

  @ApiPropertyOptional({ example: 'Decide how to allocate the Q4 budget across departments' })
  @IsString()
  @IsOptional()
  contextPrompt?: string;

  @ApiPropertyOptional({ example: '2025-12-31T23:59:59Z' })
  @IsString()
  @IsOptional()
  deadline?: string;
}

export class UpdateDecisionDto {
  @ApiPropertyOptional({ example: 'Updated Q4 Budget Allocation' })
  @IsString()
  @IsOptional()
  title?: string;

  @ApiPropertyOptional({ example: 'Updated context prompt' })
  @IsString()
  @IsOptional()
  contextPrompt?: string;

  @ApiPropertyOptional({ example: '2026-01-31T23:59:59Z' })
  @IsString()
  @IsOptional()
  deadline?: string;
}
