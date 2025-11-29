import { useState, useRef } from 'react'
import './App.css'
import ReactMarkdown from 'react-markdown'

function App() {
  const [topic, setTopic] = useState('')
  const [manual, setManual] = useState('')
  const [images, setImages] = useState([])
  const [loading, setLoading] = useState(false)
  const [files, setFiles] = useState([])
  const [isRecording, setIsRecording] = useState(false)
  const [recordingType, setRecordingType] = useState(null)
  const [cameraActive, setCameraActive] = useState(false)

  const mediaRecorderRef = useRef(null)
  const videoRef = useRef(null)
  const canvasRef = useRef(null)
  const streamRef = useRef(null)
  const chunksRef = useRef([])

  const handleFileChange = (e) => {
    setFiles(prev => [...prev, ...e.target.files])
  }

  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index))
  }

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
      setIsRecording(false)
      setRecordingType(null)
    }
  }

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
        const file = new File([blob], `photo_${Date.now()}.jpg`, { type: 'image/jpeg' })
        setFiles(prev => [...prev, file])
        stopMediaStream()
        setCameraActive(false)
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
    setLoading(true)
    setManual('')
    setImages([])

    try {
      const formData = new FormData()
      formData.append('topic', topic)
      formData.append('generate_images', 'true')

      files.forEach(file => {
        formData.append('files', file)
      })

      const response = await fetch('http://127.0.0.1:8000/generate-manual', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      setManual(data.markdown)
      setImages(data.images || [])
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

        <div className="media-controls">
          <div className="file-inputs">
            <label className="btn secondary">
              Upload Files
              <input
                type="file"
                multiple
                onChange={handleFileChange}
                accept="video/*,audio/*,image/*,.pdf,.txt"
                style={{ display: 'none' }}
              />
            </label>
          </div>

          {!isRecording && !cameraActive && (
            <>
              <button className="btn secondary" onClick={startAudioRecording}>Record Audio</button>
              <button className="btn secondary" onClick={startVideoRecording}>Record Video</button>
              <button className="btn secondary" onClick={startCamera}>Take Photo</button>
            </>
          )}

          {isRecording && (
            <button className="btn danger" onClick={stopRecording}>
              Stop Recording ({recordingType})
            </button>
          )}

          {cameraActive && (
            <div className="camera-controls">
              <button className="btn primary" onClick={takePhoto}>Capture</button>
              <button className="btn danger" onClick={stopMediaStream}>Cancel</button>
            </div>
          )}
        </div>

        {(isRecording && recordingType === 'video' || cameraActive) && (
          <div className="video-preview">
            <video ref={videoRef} autoPlay muted playsInline />
          </div>
        )}

        <canvas ref={canvasRef} style={{ display: 'none' }} />

        {files.length > 0 && (
          <div className="file-list">
            <h3>Attached Files:</h3>
            <ul>
              {files.map((file, index) => (
                <li key={index}>
                  {file.name} ({Math.round(file.size / 1024)} KB)
                  <button className="btn-small danger" onClick={() => removeFile(index)}>X</button>
                </li>
              ))}
            </ul>
          </div>
        )}

        <button className="btn primary main-action" onClick={generateManual} disabled={loading || !topic}>
          {loading ? 'Generating...' : 'Generate Manual'}
        </button>
      </div>

      <div className="manual-output">
        {manual && <ReactMarkdown>{manual}</ReactMarkdown>}

        {images.length > 0 && (
          <div className="generated-images">
            <h2>Generated Illustrations</h2>
            <div className="image-grid">
              {images.map((img, index) => (
                img && <img key={index} src={img} alt={`Illustration ${index + 1}`} />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
