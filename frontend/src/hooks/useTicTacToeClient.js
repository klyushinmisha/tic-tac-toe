import { useState } from 'react'
import { SERVER_URL } from '../config'

class TicTacToeClientError extends Error {
  constructor(error) {
    super(`TicTacToeClient request raised an error: ${error}`)
  }
}

class TicTacToeClient {
  constructor() {
    const API_VERSION = ''

    this.apiPrefix = SERVER_URL + API_VERSION
  }

  async createSession(field) {
    const resp = await fetch(this.apiPrefix + '/sessions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        field,
      }),
    })
    const payload = await resp.json()
    if (payload.error) {
      throw new TicTacToeClientError(payload.error)
    }
    return payload
  }
}

function useTicTacToeClient() {
  const [client] = useState(new TicTacToeClient())

  return client
}

export { useTicTacToeClient }
