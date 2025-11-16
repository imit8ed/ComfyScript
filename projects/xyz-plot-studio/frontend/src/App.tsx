/**
 * Main App Component
 */

import React from 'react'
import { ExperimentBuilder } from './components/ExperimentBuilder'
import './index.css'

function App() {
  return (
    <div className="App min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-900">
            XYZ Plot Studio
          </h1>
          <p className="text-sm text-gray-600">
            Systematic hyperparameter exploration for ComfyUI
          </p>
        </div>
      </header>

      <main className="py-8">
        <ExperimentBuilder />
      </main>

      <footer className="bg-white border-t mt-12">
        <div className="max-w-7xl mx-auto px-4 py-6 text-center text-sm text-gray-600">
          <p>
            Powered by <strong>ComfyScript</strong> | Built with React + FastAPI
          </p>
        </div>
      </footer>
    </div>
  )
}

export default App
