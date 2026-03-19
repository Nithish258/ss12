import {
  Controller,
  Post,
  Delete,
  Param,
  Body,
  Req,
} from '@nestjs/common';
import {
  ApiTags,
  ApiOperation,
  ApiResponse,
  ApiBearerAuth,
} from '@nestjs/swagger';
import { ParticipantsService } from './participants.service';
import { InviteParticipantDto } from './dto/participant.dto';

@ApiTags('Participants')
@ApiBearerAuth()
@Controller('api/v1/decisions/:id/participants')
export class ParticipantsController {
  constructor(private readonly participantsService: ParticipantsService) {}

  @Post()
  @ApiOperation({ summary: 'Invite a participant to a decision (owner only)' })
  @ApiResponse({ status: 201, description: 'Participant invited' })
  @ApiResponse({ status: 404, description: 'Decision or user not found' })
  @ApiResponse({ status: 409, description: 'User already a participant' })
  @ApiResponse({ status: 403, description: 'Not the owner' })
  async invite(
    @Param('id') decisionId: string,
    @Body() dto: InviteParticipantDto,
    @Req() req: any,
  ) {
    return this.participantsService.invite(decisionId, dto, req.user.sub);
  }

  @Delete(':userId')
  @ApiOperation({ summary: 'Remove a participant from a decision (owner only)' })
  @ApiResponse({ status: 200, description: 'Participant removed' })
  @ApiResponse({ status: 403, description: 'Not the owner or self-removal' })
  @ApiResponse({ status: 404, description: 'Decision or participant not found' })
  async remove(
    @Param('id') decisionId: string,
    @Param('userId') userId: string,
    @Req() req: any,
  ) {
    return this.participantsService.remove(decisionId, userId, req.user.sub);
  }
}
