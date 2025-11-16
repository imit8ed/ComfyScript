/**
 * API client for XYZ Plot Studio backend
 */

import axios, { AxiosInstance } from 'axios'
import type {
  AvailableEnums,
  Experiment,
  ExperimentCreate,
} from '@/types'

class APIClient {
  private client: AxiosInstance

  constructor(baseURL: string = '/api/v1') {
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    })
  }

  // Health
  async health() {
    const response = await this.client.get('/health')
    return response.data
  }

  // Enums
  async getAllEnums(): Promise<AvailableEnums> {
    const response = await this.client.get('/enums')
    return response.data
  }

  async getEnumValues(enumName: string): Promise<string[]> {
    const response = await this.client.get(`/enums/${enumName}`)
    return response.data.values
  }

  // Code Generation
  async generateCode(
    parameterGrid: any,
    workflowConfig: any
  ): Promise<{ code: string; workflow_json: any }> {
    const response = await this.client.post('/code/generate', {
      parameter_grid: parameterGrid,
      workflow_config: workflowConfig,
    })
    return response.data
  }

  // Experiments
  async createExperiment(experiment: ExperimentCreate): Promise<Experiment> {
    const response = await this.client.post('/experiments', experiment)
    return response.data
  }

  async getExperiment(experimentId: string): Promise<Experiment> {
    const response = await this.client.get(`/experiments/${experimentId}`)
    return response.data
  }

  async listExperiments(): Promise<Experiment[]> {
    const response = await this.client.get('/experiments')
    return response.data
  }

  async executeExperiment(experimentId: string): Promise<void> {
    await this.client.post(`/experiments/${experimentId}/execute`)
  }

  async cancelExperiment(experimentId: string): Promise<void> {
    await this.client.post(`/experiments/${experimentId}/cancel`)
  }

  // W&B
  async syncToWandB(
    experimentId: string,
    options?: {
      project?: string
      entity?: string
      tags?: string[]
    }
  ): Promise<{ run_id: string; run_url: string }> {
    const response = await this.client.post('/wandb/sync', {
      experiment_id: experimentId,
      wandb_project: options?.project,
      wandb_entity: options?.entity,
      tags: options?.tags || [],
    })
    return response.data
  }

  // WebSocket
  createWebSocket(experimentId: string): WebSocket {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const baseURL = this.client.defaults.baseURL ?? ''
    const basePath = baseURL.startsWith('http')
      ? new URL(baseURL).pathname
      : baseURL
    const normalizedBasePath = basePath.endsWith('/')
      ? basePath.slice(0, -1)
      : basePath
    const wsPath = `${normalizedBasePath}/ws/experiments/${experimentId}`
    const prefixedPath = wsPath.startsWith('/') ? wsPath : `/${wsPath}`
    const wsUrl = `${protocol}//${window.location.host}${prefixedPath}`
    return new WebSocket(wsUrl)
  }
}

export const apiClient = new APIClient()
