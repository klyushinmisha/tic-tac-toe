const SERVER_URL = process.env.REACT_APP_SERVER_URL || 'http://localhost:8000'
const WS_SERVER_URL =
  process.env.REACT_APP_WS_SERVER_URL || 'ws://localhost:8000'
const PAGE_URL = process.env.REACT_APP_PAGE_URL || 'http://localhost:3000'

export { SERVER_URL, WS_SERVER_URL, PAGE_URL }
