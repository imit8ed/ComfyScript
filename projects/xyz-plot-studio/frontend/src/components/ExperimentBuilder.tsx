/**
 * Experiment Builder Component
 *
 * Main UI for creating XYZ plot experiments.
 * Allows users to define parameter grids and workflow configurations.
 */

import React, { useState, useEffect } from 'react'
import { apiClient } from '@/services/api'
import { ParameterControl } from './ParameterControl'
import {
  ParameterType,
  ParameterDefinition,
  ParameterGrid,
  WorkflowConfig,
  WorkflowTemplate,
  ExperimentCreate,
  AvailableEnums,
} from '@/types'

export const ExperimentBuilder: React.FC = () => {
  const [enums, setEnums] = useState<AvailableEnums | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Parameter definitions
  const [xAxis, setXAxis] = useState<ParameterDefinition | null>(null)
  const [yAxis, setYAxis] = useState<ParameterDefinition | null>(null)
  const [zAxis, setZAxis] = useState<ParameterDefinition | null>(null)

  // Workflow config
  const [workflowConfig, setWorkflowConfig] = useState<Partial<WorkflowConfig>>({
    template: WorkflowTemplate.TXT2IMG,
    prompt: 'A beautiful landscape, highly detailed',
    negative_prompt: 'low quality, blurry',
    checkpoint: '',
    width: 512,
    height: 512,
    seed: 42,
    batch_size: 1,
  })

  // Experiment metadata
  const [experimentName, setExperimentName] = useState('My XYZ Plot')
  const [experimentDescription, setExperimentDescription] = useState('')

  // Load enums on mount
  useEffect(() => {
    loadEnums()
  }, [])

  const loadEnums = async () => {
    try {
      const data = await apiClient.getAllEnums()
      setEnums(data)

      // Set default checkpoint if available
      if (data.checkpoints.length > 0) {
        setWorkflowConfig((prev) => ({
          ...prev,
          checkpoint: data.checkpoints[0],
        }))
      }
    } catch (err) {
      setError('Failed to load enums from backend')
      console.error(err)
    }
  }

  const handleCreateExperiment = async () => {
    if (!xAxis || !yAxis || !zAxis) {
      setError('Please define all three axes (X, Y, Z)')
      return
    }

    if (!workflowConfig.checkpoint) {
      setError('Please select a checkpoint')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const experiment: ExperimentCreate = {
        name: experimentName,
        description: experimentDescription,
        parameter_grid: {
          x_axis: xAxis,
          y_axis: yAxis,
          z_axis: zAxis,
        },
        workflow_config: workflowConfig as WorkflowConfig,
        enable_wandb: false,
      }

      const created = await apiClient.createExperiment(experiment)

      // Execute immediately
      await apiClient.executeExperiment(created.id)

      alert(`Experiment created and started: ${created.id}`)

      // Navigate to results (in real app, use router)
      window.location.href = `/experiment/${created.id}`
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create experiment')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const totalCombinations =
    (xAxis?.values.length || 0) *
    (yAxis?.values.length || 0) *
    (zAxis?.values.length || 0)

  return (
    <div className="experiment-builder max-w-6xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Create XYZ Plot Experiment</h1>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {/* Experiment Info */}
      <div className="mb-6 space-y-3">
        <div>
          <label className="block text-sm font-medium mb-1">Experiment Name</label>
          <input
            type="text"
            value={experimentName}
            onChange={(e) => setExperimentName(e.target.value)}
            className="w-full px-3 py-2 border rounded"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Description</label>
          <textarea
            value={experimentDescription}
            onChange={(e) => setExperimentDescription(e.target.value)}
            className="w-full px-3 py-2 border rounded"
            rows={2}
          />
        </div>
      </div>

      {/* Parameter Grid Definition */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <ParameterControl
          label="X-Axis: CFG Scale"
          parameterName="cfg"
          type={ParameterType.NUMERIC}
          onChange={setXAxis}
        />
        <ParameterControl
          label="Y-Axis: Steps"
          parameterName="steps"
          type={ParameterType.NUMERIC}
          onChange={setYAxis}
        />
        <ParameterControl
          label="Z-Axis: Sampler"
          parameterName="sampler_name"
          type={ParameterType.ENUM}
          availableValues={enums?.samplers || []}
          onChange={setZAxis}
        />
      </div>

      {/* Workflow Configuration */}
      <div className="border rounded-lg p-4 mb-6">
        <h2 className="text-xl font-semibold mb-4">Workflow Configuration</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Checkpoint</label>
            <select
              value={workflowConfig.checkpoint}
              onChange={(e) =>
                setWorkflowConfig({ ...workflowConfig, checkpoint: e.target.value })
              }
              className="w-full px-3 py-2 border rounded"
            >
              <option value="">Select checkpoint...</option>
              {enums?.checkpoints.map((checkpoint) => (
                <option key={checkpoint} value={checkpoint}>
                  {checkpoint}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Seed</label>
            <input
              type="number"
              value={workflowConfig.seed}
              onChange={(e) =>
                setWorkflowConfig({
                  ...workflowConfig,
                  seed: parseInt(e.target.value),
                })
              }
              className="w-full px-3 py-2 border rounded"
            />
          </div>

          <div className="md:col-span-2">
            <label className="block text-sm font-medium mb-1">Prompt</label>
            <textarea
              value={workflowConfig.prompt}
              onChange={(e) =>
                setWorkflowConfig({ ...workflowConfig, prompt: e.target.value })
              }
              className="w-full px-3 py-2 border rounded"
              rows={3}
            />
          </div>

          <div className="md:col-span-2">
            <label className="block text-sm font-medium mb-1">Negative Prompt</label>
            <textarea
              value={workflowConfig.negative_prompt}
              onChange={(e) =>
                setWorkflowConfig({
                  ...workflowConfig,
                  negative_prompt: e.target.value,
                })
              }
              className="w-full px-3 py-2 border rounded"
              rows={2}
            />
          </div>
        </div>
      </div>

      {/* Summary and Create */}
      <div className="border rounded-lg p-4 bg-blue-50">
        <h3 className="font-semibold mb-2">Experiment Summary</h3>
        <div className="text-sm space-y-1">
          <div>
            <strong>Total Combinations:</strong> {totalCombinations}
          </div>
          <div>
            <strong>Estimated Time:</strong>{' '}
            {Math.ceil((totalCombinations * 20) / 60)} minutes
          </div>
        </div>

        <button
          onClick={handleCreateExperiment}
          disabled={loading || !xAxis || !yAxis || !zAxis}
          className="mt-4 w-full px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {loading ? 'Creating...' : 'Create and Start Experiment'}
        </button>
      </div>
    </div>
  )
}

export default ExperimentBuilder
