import { useState } from 'react'
import { TicTacToeClient } from '../ticTacToeClient'

function useTicTacToeClient() {
  const [client] = useState(new TicTacToeClient())

  return client
}

export { useTicTacToeClient }
