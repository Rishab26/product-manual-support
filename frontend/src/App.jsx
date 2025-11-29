import { useState } from 'react'
import './App.css'
import ReactMarkdown from 'react-markdown'

function App() {
  const [topic, setTopic] = useState('')
  const [manual, setManual] = useState('')
  const [loading, setLoading] = useState(false)

  const generateManual = async () => {
    setLoading(true)
    setManual('')
    try {
      const response = await fetch('http://127.0.0.1:8000/generate-manual', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ topic }),
      })
      const data = await response.json()
      setManual(data.manual)
    } catch (error) {
      console.error('Error generating manual:', error)
      setManual('Error generating manual. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <h1>AI Manual Generator</h1>
      <div className="input-group">
        <input
          type="text"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="Enter topic (e.g., How to assemble a table)"
        />
        <button onClick={generateManual} disabled={loading || !topic}>
          {loading ? 'Generating...' : 'Generate Manual'}
        </button>
      </div>
      <div className="manual-output">
        {manual && <ReactMarkdown>{manual}</ReactMarkdown>}
      </div>
    </div>
  )
}

export default App
