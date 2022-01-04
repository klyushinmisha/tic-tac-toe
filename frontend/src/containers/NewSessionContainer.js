import { useToast } from '@chakra-ui/react'
import React, { useState } from 'react'
import { useTicTacToeClient } from '../hooks/useTicTacToeClient'
import { useUILocker } from '../hooks/useUILocker'
import { CreatedSessionLink, CreateSessionForm } from '../components/Session'

function NewSessionContainer() {
  const [session, setSession] = useState(null)
  const [lockUI, withUILock] = useUILocker()
  const client = useTicTacToeClient()
  const toast = useToast()

  const handleCreate = withUILock(async ({ field }) => {
    const DEFAULT_TOAST_DURATION_MS = 3000

    try {
      setSession(await client.createSession(field))
    } catch {
      toast({
        title: 'Session creation error',
        description: 'Failed to create new session',
        status: 'error',
        duration: DEFAULT_TOAST_DURATION_MS,
        isClosable: true,
      })
    }
  })

  return (
    <>
      {session && <CreatedSessionLink sessionId={session.id} />}
      <CreateSessionForm disabled={lockUI} handleCreate={handleCreate} />
    </>
  )
}

export { NewSessionContainer }
