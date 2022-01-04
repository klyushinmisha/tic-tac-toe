import { useState } from 'react'

function useUILocker() {
  const [count, setCount] = useState(0)

  const lock = () => setCount((count) => count + 1)
  const unlock = () => setCount((count) => count - 1)

  const withUILock = function (cb) {
    return async function (...args) {
      lock()
      try {
        await cb(...args)
      } finally {
        unlock()
      }
    }
  }

  const lockUI = count !== 0

  return [lockUI, withUILock]
}

export { useUILocker }
