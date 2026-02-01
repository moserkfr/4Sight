import React from 'react'
import { useNavigate } from 'react-router-dom'
import './App.css'

const App: React.FC = () => {
  const navigate = useNavigate()

  return (
    <div className="app">
      <div className="overlay"></div>
      <header className="header">
        <h1>4Sight</h1>
        <p className="tagline">Advancing SDG 4 with Smart Vision</p>
      </header>

      <main className="main-content">
        <section className="intro">
          <p>
            4Sight integrates AI-powered facial recognition into smart glasses,
            automating attendance for educational institutions. Designed around{' '}
            <br />
            <strong>SDG 4: Quality Education</strong>, our hands-free system
            captures and logs student data in real-time via ESP32-CAM, paired
            with a scalable analytics dashboard.
          </p>
        </section>

        <button 
          className="cta-button" 
          onClick={() => navigate('/dashboard')}
        >
          View Attendance Dashboard →
        </button>
      </main>
    </div>
  )
}

export default App