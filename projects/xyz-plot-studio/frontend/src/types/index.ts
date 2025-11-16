/**
 * TypeScript types for XYZ Plot Studio
 */

export enum ExperimentStatus {
  DRAFT = 'draft',
  QUEUED = 'queued',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled',
}

export enum ParameterType {
  NUMERIC = 'numeric',
  CATEGORICAL = 'categorical',
  ENUM = 'enum',
}

export enum WorkflowTemplate {
  TXT2IMG = 'txt2img',
  IMG2IMG = 'img2img',
  HIRES_FIX = 'hires_fix',
  LORA_COMPARISON = 'lora_comparison',
  CUSTOM = 'custom',
}

export interface ParameterDefinition {
  name: string
  display_name: string
  type: ParameterType
  values: (number | string)[]
}

export interface ParameterGrid {
  x_axis: ParameterDefinition
  y_axis: ParameterDefinition
  z_axis: ParameterDefinition
}

export interface WorkflowConfig {
  template: WorkflowTemplate
  prompt: string
  negative_prompt: string
  checkpoint: string
  width: number
  height: number
  batch_size: number
  seed: number
  vae?: string
  loras?: any[]
  controlnet?: any
}

export interface ExperimentCreate {
  name: string
  description: string
  parameter_grid: ParameterGrid
  workflow_config: WorkflowConfig
  multi_seed?: boolean
  num_seeds?: number
  enable_wandb?: boolean
  wandb_tags?: string[]
}

export interface Experiment {
  id: string
  name: string
  description: string
  status: ExperimentStatus
  parameter_grid: ParameterGrid
  workflow_config: WorkflowConfig
  total_images: number
  images_generated: number
  progress: number
  created_at: string
  updated_at: string
  started_at?: string
  completed_at?: string
  error_message?: string
  wandb_run_id?: string
  wandb_run_url?: string
}

export interface GeneratedImage {
  id: string
  experiment_id: string
  parameters: Record<string, any>
  image_path: string
  thumbnail_path?: string
  seed: number
  generation_time: number
  metrics?: Record<string, number>
  created_at: string
}

export interface AvailableEnums {
  samplers: string[]
  schedulers: string[]
  checkpoints: string[]
  vaes: string[]
  loras: string[]
  upscale_models: string[]
}

export interface NumericParameterRange {
  min_value: number
  max_value: number
  step: number
  logarithmic?: boolean
}

export interface WSMessage {
  type: string
  timestamp: string
}

export interface WSImageGenerated extends WSMessage {
  type: 'image_generated'
  experiment_id: string
  image_index: number
  image_path: string
  parameters: Record<string, any>
  progress: number
}

export interface WSExperimentCompleted extends WSMessage {
  type: 'experiment_completed'
  experiment_id: string
  total_images: number
  total_time: number
}
