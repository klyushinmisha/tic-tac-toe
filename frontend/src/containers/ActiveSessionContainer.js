import React, { useState } from 'react'
import { useParams } from 'react-router-dom'
import { GameSessionContainer } from './GameSessionContainer'
import { PlayerJoinForm } from '../components'

function ActiveSessionContainer() {
  const [playerId, setPlayerId] = useState(null)
  const { sessionId } = useParams()

  const handleJoin = (player) => setPlayerId(player)

  return sessionId && playerId ? (
    <GameSessionContainer sessionId={sessionId} playerId={playerId} />
  ) : (
    <PlayerJoinForm handleJoin={handleJoin} />
  )
}

export { ActiveSessionContainer }
