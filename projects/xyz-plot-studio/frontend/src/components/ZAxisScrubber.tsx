/**
 * Z-Axis Scrubber Component
 *
 * Interactive scrubber for navigating through Z-axis values in XYZ plots.
 * Features:
 * - Slider navigation
 * - Keyboard shortcuts ([ / ])
 * - Smooth transitions
 * - Value labels
 */

import React, { useEffect, useState, useCallback } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'

interface ZAxisScrubberProps {
  zValues: (number | string)[]
  currentIndex: number
  onChange: (index: number) => void
  parameterName: string
  className?: string
}

export const ZAxisScrubber: React.FC<ZAxisScrubberProps> = ({
  zValues,
  currentIndex,
  onChange,
  parameterName,
  className = '',
}) => {
  const [localIndex, setLocalIndex] = useState(currentIndex)

  // Sync with prop changes
  useEffect(() => {
    setLocalIndex(currentIndex)
  }, [currentIndex])

  // Keyboard navigation
  useEffect(() => {
    const handleKeyPress = (event: KeyboardEvent) => {
      if (event.key === '[' || event.key === 'ArrowLeft') {
        event.preventDefault()
        handlePrevious()
      } else if (event.key === ']' || event.key === 'ArrowRight') {
        event.preventDefault()
        handleNext()
      }
    }

    window.addEventListener('keydown', handleKeyPress)
    return () => window.removeEventListener('keydown', handleKeyPress)
  }, [localIndex])

  const handlePrevious = useCallback(() => {
    if (localIndex > 0) {
      const newIndex = localIndex - 1
      setLocalIndex(newIndex)
      onChange(newIndex)
    }
  }, [localIndex, onChange])

  const handleNext = useCallback(() => {
    if (localIndex < zValues.length - 1) {
      const newIndex = localIndex + 1
      setLocalIndex(newIndex)
      onChange(newIndex)
    }
  }, [localIndex, zValues.length, onChange])

  const handleSliderChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newIndex = parseInt(event.target.value, 10)
    setLocalIndex(newIndex)
    onChange(newIndex)
  }

  const currentValue = zValues[localIndex]

  return (
    <div className={`z-axis-scrubber ${className}`}>
      <div className="scrubber-header mb-4">
        <h3 className="text-lg font-semibold text-gray-700">
          Z-Axis: {parameterName}
        </h3>
        <div className="text-sm text-gray-500">
          Use <kbd>[</kbd> and <kbd>]</kbd> keys to navigate
        </div>
      </div>

      <div className="scrubber-controls flex items-center gap-4">
        {/* Previous button */}
        <button
          onClick={handlePrevious}
          disabled={localIndex === 0}
          className="p-2 rounded-lg bg-blue-500 text-white disabled:bg-gray-300 disabled:cursor-not-allowed hover:bg-blue-600 transition-colors"
          aria-label="Previous Z value"
        >
          <ChevronLeft className="w-5 h-5" />
        </button>

        {/* Slider */}
        <div className="flex-1">
          <input
            type="range"
            min={0}
            max={zValues.length - 1}
            value={localIndex}
            onChange={handleSliderChange}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
          />

          {/* Value markers */}
          <div className="flex justify-between mt-2 text-xs text-gray-600">
            {zValues.map((value, idx) => (
              <div
                key={idx}
                className={`marker ${
                  idx === localIndex ? 'font-bold text-blue-600' : ''
                }`}
              >
                {typeof value === 'number' ? value.toFixed(2) : value}
              </div>
            ))}
          </div>
        </div>

        {/* Next button */}
        <button
          onClick={handleNext}
          disabled={localIndex === zValues.length - 1}
          className="p-2 rounded-lg bg-blue-500 text-white disabled:bg-gray-300 disabled:cursor-not-allowed hover:bg-blue-600 transition-colors"
          aria-label="Next Z value"
        >
          <ChevronRight className="w-5 h-5" />
        </button>
      </div>

      {/* Current value display */}
      <div className="scrubber-value mt-4 text-center">
        <div className="text-sm text-gray-500">Current Value</div>
        <div className="text-2xl font-bold text-blue-600">
          {typeof currentValue === 'number'
            ? currentValue.toFixed(2)
            : currentValue}
        </div>
        <div className="text-xs text-gray-400">
          {localIndex + 1} of {zValues.length}
        </div>
      </div>

      <style jsx>{`
        .slider::-webkit-slider-thumb {
          appearance: none;
          width: 20px;
          height: 20px;
          background: #3b82f6;
          border-radius: 50%;
          cursor: pointer;
        }

        .slider::-moz-range-thumb {
          width: 20px;
          height: 20px;
          background: #3b82f6;
          border-radius: 50%;
          cursor: pointer;
          border: none;
        }

        kbd {
          padding: 2px 6px;
          background: #f3f4f6;
          border: 1px solid #d1d5db;
          border-radius: 3px;
          font-family: monospace;
          font-size: 0.85em;
        }
      `}</style>
    </div>
  )
}

export default ZAxisScrubber
