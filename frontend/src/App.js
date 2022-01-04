import './App.css'
import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { NewSessionContainer } from './containers/NewSessionContainer'
import { ActiveSessionContainer } from './containers/ActiveSessionContainer'

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
