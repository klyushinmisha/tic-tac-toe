import { useEffect, useState } from 'react'
import { WS_SERVER_URL } from '../config'

function useWebSocketClient(sessionId, playerId, handleMessage) {
  const [ws, setWs] = useState(null)
  const [active, setActive] = useState(false)

  useEffect(() => {
    const ws = new WebSocket(
      `${WS_SERVER_URL}/sessions/${sessionId}/players/${playerId}/join`
    )

    ws.onmessage = (e) => {
      handleMessage(JSON.parse(e.data))
    }

    ws.onopen = () => setActive(true)
    ws.onclose = () => setActive(false)

    setWs(ws)

    return () => ws.close()
  }, [sessionId, playerId, setWs, handleMessage])

  const sendJSON = async (data) => {
    await ws.send(JSON.stringify(data))
  }
  const noopSender = () => {}

  return active ? sendJSON : noopSender
}

export { useWebSocketClient }
