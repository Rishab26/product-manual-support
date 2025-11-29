import { useState, useRef, useEffect } from 'react'
import './App.css'
import ReactMarkdown from 'react-markdown'
import {
  Mic,
  Video,
  Camera,
  Upload,
  X,
  FileText,
  ArrowRight,
  RotateCcw,
  StopCircle
} from 'lucide-react'

const LOADING_SENTENCES = [
  "Consulting the oracle of knowledge...",
  "Summoning the spirits of clarity...",
  "Weaving words into wisdom...",
  "Decoding the matrix of instructions...",
  "Polishing the gems of guidance...",
  "Constructing the pillars of understanding...",
  "Filtering the noise, keeping the signal...",
  "Translating thoughts into actions...",
  "Harmonizing the elements of the manual...",
  "Preparing the blueprint for success..."
]

function App() {
  // Stages: 'input', 'processing', 'result'
  const [stage, setStage] = useState('input')

  const [topic, setTopic] = useState('')
  const [manual, setManual] = useState('')
  const [files, setFiles] = useState([])
  const [loadingText, setLoadingText] = useState(LOADING_SENTENCES[0])

  // Media State
  const [isRecording, setIsRecording] = useState(false)
  const [recordingType, setRecordingType] = useState(null) // 'audio', 'video'
  const [cameraActive, setCameraActive] = useState(false)

  const mediaRecorderRef = useRef(null)
  const videoRef = useRef(null)
  const canvasRef = useRef(null)
  const streamRef = useRef(null)
  const chunksRef = useRef([])

  // Abort Controller for cancellation
  const abortControllerRef = useRef(null)

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopMediaStream()
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
    }
  }, [])

  // Cycle loading sentences
  useEffect(() => {
    let interval;
    if (stage === 'processing') {
      setLoadingText(LOADING_SENTENCES[0])
      let index = 0;
      interval = setInterval(() => {
        index = (index + 1) % LOADING_SENTENCES.length;
        setLoadingText(LOADING_SENTENCES[index]);
      }, 2000);
    }
    return () => clearInterval(interval);
  }, [stage]);

  const handleFileChange = (e) => {
    if (e.target.files) {
      setFiles(prev => [...prev, ...Array.from(e.target.files)])
    }
  }

  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index))
  }

  // Audio Recording
  const startAudioRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      streamRef.current = stream
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder
      chunksRef.current = []

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data)
      }

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' })
        const file = new File([blob], `audio_recording_${Date.now()}.webm`, { type: 'audio/webm' })
        setFiles(prev => [...prev, file])
        stopMediaStream()
      }

      mediaRecorder.start()
      setIsRecording(true)
      setRecordingType('audio')
    } catch (err) {
      console.error("Error accessing microphone:", err)
      alert("Could not access microphone")
    }
  }

  // Video Recording
  const startVideoRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true })
      streamRef.current = stream
      if (videoRef.current) {
        videoRef.current.srcObject = stream
      }

      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder
      chunksRef.current = []

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data)
      }

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'video/webm' })
        const file = new File([blob], `video_recording_${Date.now()}.webm`, { type: 'video/webm' })
        setFiles(prev => [...prev, file])
        stopMediaStream()
      }

      mediaRecorder.start()
      setIsRecording(true)
      setRecordingType('video')
    } catch (err) {
      console.error("Error accessing camera/microphone:", err)
      alert("Could not access camera/microphone")
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
    }
  }

  // Photo Capture
  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true })
      streamRef.current = stream
      if (videoRef.current) {
        videoRef.current.srcObject = stream
      }
      setCameraActive(true)
    } catch (err) {
      console.error("Error accessing camera:", err)
      alert("Could not access camera")
    }
  }

  const takePhoto = () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current
      const canvas = canvasRef.current
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight

      const ctx = canvas.getContext('2d')
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height)

      canvas.toBlob((blob) => {
        if (blob) {
          const file = new File([blob], `photo_${Date.now()}.jpg`, { type: 'image/jpeg' })
          setFiles(prev => [...prev, file])
          stopMediaStream()
        }
      }, 'image/jpeg')
    }
  }

  const stopMediaStream = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop())
      streamRef.current = null
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null
    }
    setCameraActive(false)
    setIsRecording(false)
    setRecordingType(null)
  }

  const generateManual = async () => {
    if (!topic.trim() && files.length === 0) {
      alert('Please enter a topic or upload/record media to generate a manual.')
      return
    }

    setStage('processing')
    setManual('')

    // Create new AbortController
    abortControllerRef.current = new AbortController()

    try {
      let response;
      const formData = new FormData()
      formData.append('topic', topic)

      files.forEach(file => {
        formData.append('files', file)
      })

      response = await fetch('/generate-manual', {
        method: 'POST',
        body: formData,
        signal: abortControllerRef.current.signal
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      setManual(data.manual)
      setStage('result')
    } catch (error) {
      if (error.name === 'AbortError') {
        console.log('Generation cancelled')
        // Stay in input stage or handle as needed, but we usually reset to input on cancel
        setStage('input')
      } else {
        console.error('Error generating manual:', error)
        alert('Error generating manual. Please try again.')
        setStage('input')
      }
    } finally {
      abortControllerRef.current = null
    }
  }

  const cancelGeneration = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }
  }

  const resetApp = () => {
    setTopic('')
    setFiles([])
    setManual('')
    setStage('input')
  }

  const handleKeyDown = (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
      generateManual()
    }
  }

  // Render Helpers
  const renderInputStage = () => (
    <div className="input-stage fade-in">
      <div className="topic-input-container">
        <input
          type="text"
          className="topic-input"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="What do you want to learn?"
          autoFocus
        />
      </div>

      <div className="media-grid">
        <label className="media-btn">
          <Upload />
          <span>Upload</span>
          <input
            type="file"
            multiple
            onChange={handleFileChange}
            accept="video/*,audio/*,image/*,.pdf,.txt"
            style={{ display: 'none' }}
          />
        </label>

        <button className="media-btn" onClick={startAudioRecording}>
          <Mic />
          <span>Record Audio</span>
        </button>

        <button className="media-btn" onClick={startVideoRecording}>
          <Video />
          <span>Record Video</span>
        </button>

        <button className="media-btn" onClick={startCamera}>
          <Camera />
          <span>Take Photo</span>
        </button>
      </div>

      {files.length > 0 && (
        <div className="file-list">
          {files.map((file, index) => (
            <div key={index} className="file-item slide-in">
              <div className="file-info">
                <FileText size={16} className="text-secondary" />
                <span className="file-name">{file.name}</span>
              </div>
              <button className="remove-btn" onClick={() => removeFile(index)}>
                <X size={16} />
              </button>
            </div>
          ))}
        </div>
      )}

      <button
        className="btn-primary"
        onClick={generateManual}
      >
        Generate Manual
      </button>
    </div>
  )

  const renderProcessingStage = () => (
    <div className="processing-stage fade-in">
      <div className="spinner"></div>
      <p className="loading-text fade-in-text">{loadingText}</p>
      <button className="btn-secondary" onClick={cancelGeneration} style={{ marginTop: '1rem' }}>
        Cancel
      </button>
    </div>
  )

  // Custom component to render manual in two-column layout
  const ManualRenderer = ({ markdown }) => {
    // Parse markdown into sections based on h2 headers
    const sections = []
    const lines = markdown.split('\n')
    let currentSection = { title: '', content: [], image: null }

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i]

      // Check if this is an h2 header (section start)
      if (line.startsWith('## ')) {
        // Save previous section if it has content
        if (currentSection.title || currentSection.content.length > 0) {
          sections.push({ ...currentSection })
        }
        // Start new section
        currentSection = {
          title: line.replace('## ', ''),
          content: [],
          image: null
        }
      }
      // Check if this is an image
      else if (line.match(/!\[.*\]\(.*\)/)) {
        const match = line.match(/!\[(.*)\]\((.*)\)/)
        if (match) {
          currentSection.image = {
            alt: match[1],
            src: match[2]
          }
        }
      }
      // Regular content
      else if (line.trim()) {
        currentSection.content.push(line)
      }
    }

    // Don't forget the last section
    if (currentSection.title || currentSection.content.length > 0) {
      sections.push(currentSection)
    }

    return (
      <div>
        {sections.map((section, index) => (
          <div key={index} className="manual-section">
            <div className="manual-section-text">
              {section.title && <h2>{section.title}</h2>}
              <ReactMarkdown>{section.content.join('\n')}</ReactMarkdown>
            </div>
            {index !== 0 && (
              <div className="manual-section-image">
                {section.image ? (
                  <img
                    src={section.image.src}
                    alt={section.image.alt}
                  />
                ) : (
                  <div style={{
                    color: 'var(--text-tertiary)',
                    textAlign: 'center',
                    padding: '2rem'
                  }}>
                    No image for this section
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    )
  }

  const renderResultStage = () => (
    <div className="result-stage animate-slide-up">
      <div className="manual-content">
        <ManualRenderer markdown={manual} />
      </div>
      <button className="btn-secondary" onClick={resetApp}>
        <RotateCcw size={16} />
        New Manual
      </button>
    </div>
  )

  return (
    <div className="app-container">
      {stage === 'input' && (
        <>
          <h1>Manual Generator</h1>
          <p className="subtitle">Create clear, step-by-step guides instantly.</p>
        </>
      )}

      {stage === 'input' && renderInputStage()}
      {stage === 'processing' && renderProcessingStage()}
      {stage === 'result' && renderResultStage()}

      {/* Overlays for Active Recording/Camera */}
      {isRecording && (
        <div className="recording-overlay">
          <div className="recording-indicator"></div>
          <span>Recording {recordingType}...</span>
          <button onClick={stopRecording}>
            <StopCircle fill="white" size={32} />
          </button>
        </div>
      )}

      {cameraActive && !isRecording && (
        <div className="fixed inset-0 bg-black z-50 flex flex-col items-center justify-center p-4" style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'black', zIndex: 100 }}>
          <div className="video-preview-container">
            <video ref={videoRef} autoPlay muted playsInline />
            <button className="capture-btn" onClick={takePhoto}></button>
          </div>
          <button
            className="absolute top-4 right-4 text-white p-2"
            style={{ position: 'absolute', top: '1rem', right: '1rem', color: 'white' }}
            onClick={stopMediaStream}
          >
            <X size={32} />
          </button>
        </div>
      )}

      {/* Hidden canvas for photo capture */}
      <canvas ref={canvasRef} style={{ display: 'none' }} />
    </div>
  )
}

export default App
