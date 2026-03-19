import {
  Controller,
  Get,
  Post,
  Patch,
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
import { DecisionsService } from './decisions.service';
import { CreateDecisionDto, UpdateDecisionDto } from './dto/decision.dto';

@ApiTags('Decisions')
@ApiBearerAuth()
@Controller('api/v1/decisions')
export class DecisionsController {
  constructor(private readonly decisionsService: DecisionsService) {}

  @Post()
  @ApiOperation({ summary: 'Create a new decision' })
  @ApiResponse({ status: 201, description: 'Decision created' })
  async create(@Body() dto: CreateDecisionDto, @Req() req: any) {
    return this.decisionsService.create(dto, req.user.sub);
  }

  @Get()
  @ApiOperation({ summary: 'List all decisions where user is a participant' })
  @ApiResponse({ status: 200, description: 'List of decisions' })
  async findAll(@Req() req: any) {
    return this.decisionsService.findAll(req.user.sub);
  }

  @Get(':id')
  @ApiOperation({ summary: 'Get a decision by ID' })
  @ApiResponse({ status: 200, description: 'Decision details' })
  @ApiResponse({ status: 404, description: 'Decision not found' })
  @ApiResponse({ status: 403, description: 'Not a participant' })
  async findOne(@Param('id') id: string, @Req() req: any) {
    return this.decisionsService.findOne(id, req.user.sub);
  }

  @Patch(':id')
  @ApiOperation({ summary: 'Update a decision (owner only, DRAFT status only)' })
  @ApiResponse({ status: 200, description: 'Decision updated' })
  @ApiResponse({ status: 403, description: 'Not owner or not in DRAFT' })
  @ApiResponse({ status: 404, description: 'Decision not found' })
  async update(
    @Param('id') id: string,
    @Body() dto: UpdateDecisionDto,
    @Req() req: any,
  ) {
    return this.decisionsService.update(id, dto, req.user.sub);
  }
}
