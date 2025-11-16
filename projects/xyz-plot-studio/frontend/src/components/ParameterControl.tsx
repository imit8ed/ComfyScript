/**
 * Parameter Control Component
 *
 * Configurable control for defining parameter sweep ranges.
 * Supports numeric ranges and categorical/enum selections.
 */

import React, { useState } from 'react'
import { ParameterType, ParameterDefinition } from '@/types'

interface ParameterControlProps {
  label: string
  parameterName: string
  type: ParameterType
  availableValues?: string[]
  onChange: (definition: ParameterDefinition) => void
  className?: string
}

export const ParameterControl: React.FC<ParameterControlProps> = ({
  label,
  parameterName,
  type,
  availableValues = [],
  onChange,
  className = '',
}) => {
  const [minValue, setMinValue] = useState<number>(1)
  const [maxValue, setMaxValue] = useState<number>(10)
  const [step, setStep] = useState<number>(1)
  const [selectedValues, setSelectedValues] = useState<string[]>([])

  const handleNumericUpdate = () => {
    const values: number[] = []
    for (let i = minValue; i <= maxValue; i += step) {
      values.push(i)
    }

    onChange({
      name: parameterName,
      display_name: label,
      type: ParameterType.NUMERIC,
      values,
    })
  }

  const handleCategoricalUpdate = () => {
    onChange({
      name: parameterName,
      display_name: label,
      type,
      values: selectedValues,
    })
  }

  const toggleValue = (value: string) => {
    setSelectedValues((prev) => {
      const newValues = prev.includes(value)
        ? prev.filter((v) => v !== value)
        : [...prev, value]

      // Auto-update on change
      setTimeout(() => {
        onChange({
          name: parameterName,
          display_name: label,
          type,
          values: newValues,
        })
      }, 0)

      return newValues
    })
  }

  return (
    <div className={`parameter-control border rounded-lg p-4 ${className}`}>
      <h3 className="font-semibold mb-3">{label}</h3>

      {type === ParameterType.NUMERIC && (
        <div className="numeric-controls space-y-3">
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-sm text-gray-600 mb-1">Min</label>
              <input
                type="number"
                value={minValue}
                onChange={(e) => setMinValue(parseFloat(e.target.value))}
                onBlur={handleNumericUpdate}
                className="w-full px-3 py-2 border rounded"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-600 mb-1">Max</label>
              <input
                type="number"
                value={maxValue}
                onChange={(e) => setMaxValue(parseFloat(e.target.value))}
                onBlur={handleNumericUpdate}
                className="w-full px-3 py-2 border rounded"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-600 mb-1">Step</label>
              <input
                type="number"
                value={step}
                onChange={(e) => setStep(parseFloat(e.target.value))}
                onBlur={handleNumericUpdate}
                className="w-full px-3 py-2 border rounded"
                step="0.1"
              />
            </div>
          </div>

          <div className="text-sm text-gray-500">
            {Math.floor((maxValue - minValue) / step) + 1} values
          </div>
        </div>
      )}

      {(type === ParameterType.ENUM || type === ParameterType.CATEGORICAL) && (
        <div className="categorical-controls space-y-2">
          <div className="flex gap-2 mb-2">
            <button
              onClick={() => setSelectedValues([...availableValues])}
              className="text-sm px-3 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
            >
              Select All
            </button>
            <button
              onClick={() => setSelectedValues([])}
              className="text-sm px-3 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
            >
              Clear
            </button>
          </div>

          <div className="max-h-48 overflow-y-auto space-y-1">
            {availableValues.map((value) => (
              <label
                key={value}
                className="flex items-center gap-2 p-2 hover:bg-gray-50 rounded cursor-pointer"
              >
                <input
                  type="checkbox"
                  checked={selectedValues.includes(value)}
                  onChange={() => toggleValue(value)}
                  className="w-4 h-4"
                />
                <span className="text-sm">{value}</span>
              </label>
            ))}
          </div>

          <div className="text-sm text-gray-500 mt-2">
            {selectedValues.length} selected
          </div>
        </div>
      )}
    </div>
  )
}

export default ParameterControl
