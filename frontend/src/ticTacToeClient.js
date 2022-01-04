import { SERVER_URL } from './config'

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
      throw Error(payload.error)
    }
    return payload
  }
}

export { TicTacToeClient }
