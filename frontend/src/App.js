import './App.css'
import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { NewSessionContainer, ActiveSessionContainer } from './containers'

function App() {
  // TODO: add default route
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/sessions/:sessionId"
          element={<ActiveSessionContainer />}
        />
        <Route path="" element={<NewSessionContainer />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
