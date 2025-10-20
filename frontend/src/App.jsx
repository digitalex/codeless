import React, { useState } from 'react'
import Editor from '@monaco-editor/react'
import axios from 'axios'
import './App.css'

function App() {
  const [interfaceCode, setInterfaceCode] = useState(`from abc import ABC, abstractmethod

class Calculator(ABC):
    @abstractmethod
    def add(a: int, b: int) -> int:
        """Adds a and b"""
        pass

    @abstractmethod
    def subtract(a: int, b: int) -> int:
        """Subtracts b from a"""
        pass

    @abstractmethod
    def product(a: int, b: int) -> int:
        """Returns the product of a and b"""
        pass
`)
  const [testCode, setTestCode] = useState('')
  const [implCode, setImplCode] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const API_URL = 'http://localhost:8000/api'

  const generateTests = async () => {
    setLoading(true)
    setError('')
    try {
      const response = await axios.post(`${API_URL}/generate_tests`, {
        interface_str: interfaceCode,
        prior_attempts: []
      })
      setTestCode(response.data.test_code)
    } catch (err) {
      console.error(err)
      setError('Failed to generate tests: ' + (err.response?.data?.detail || err.message))
    } finally {
      setLoading(false)
    }
  }

  const generateImpl = async () => {
    setLoading(true)
    setError('')
    try {
      const response = await axios.post(`${API_URL}/generate_impl`, {
        interface_str: interfaceCode,
        test_str: testCode,
        prior_attempts: []
      })
      setImplCode(response.data.impl_code)
    } catch (err) {
      console.error(err)
      setError('Failed to generate implementation: ' + (err.response?.data?.detail || err.message))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-container">
      <h1>Codeless AI</h1>
      {error && <div className="error">{error}</div>}

      <div className="editors-row">
        <div className="editor-container">
          <h2>Interface</h2>
          <Editor
            height="400px"
            defaultLanguage="python"
            value={interfaceCode}
            onChange={setInterfaceCode}
            theme="vs-dark"
          />
        </div>
        <div className="editor-container">
          <h2>Tests</h2>
           <Editor
            height="400px"
            defaultLanguage="python"
            value={testCode}
            onChange={setTestCode}
            theme="vs-dark"
          />
        </div>
      </div>

      <div className="controls">
        <button onClick={generateTests} disabled={loading || !interfaceCode}>
          {loading ? 'Working...' : 'Generate Tests'}
        </button>
        <button onClick={generateImpl} disabled={loading || !interfaceCode || !testCode}>
          {loading ? 'Working...' : 'Generate Implementation'}
        </button>
      </div>

      <div className="impl-container">
        <h2>Implementation</h2>
        <Editor
            height="400px"
            defaultLanguage="python"
            value={implCode}
            onChange={setImplCode}
            theme="vs-dark"
          />
      </div>
    </div>
  )
}

export default App
