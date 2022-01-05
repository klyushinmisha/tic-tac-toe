import {
  Center,
  useDisclosure,
  HStack,
  VStack,
  useToast,
} from '@chakra-ui/react'
import React, { useCallback, useState } from 'react'
import { useWebSocketClient, useUILocker } from '../hooks'
import { Board, GameModal } from '../components'

function GameSessionContainer({ sessionId, playerId }) {
  const [state, setState] = useState(null)
  const { isOpen, onOpen, onClose } = useDisclosure()
  const toast = useToast()
  const [lockUI, withUILock] = useUILocker()
  const sendJSON = useWebSocketClient(
    sessionId,
    playerId,
    useCallback(
      (data) => {
        const DEFAULT_TOAST_DURATION_MS = 3000

        if (data.error) {
          toast({
            title: 'Game error',
            description: data.error,
            status: 'error',
            duration: DEFAULT_TOAST_DURATION_MS,
            isClosable: true,
          })
        } else {
          setState(data)
          if (data.game_over) {
            onOpen()
          }
        }
      },
      [toast, setState, onOpen]
    )
  )

  const handleMove = withUILock(
    async (i, j) =>
      await sendJSON({
        row: i,
        col: j,
      })
  )

  let gameOverText
  if (state?.game_over) {
    if (state.winner === null) {
      gameOverText = 'Draw!'
    } else if (state.winner === state.your_sign) {
      gameOverText = 'You win!'
    } else {
      gameOverText = 'You lose!'
    }
  }

  return (
    state && (
      <>
        <VStack alignItems="center">
          <HStack justifyItems="center" height="100vh">
            <Center>
              <Board
                state={state.state}
                disabled={!state.your_turn || state.game_over || lockUI}
                move={handleMove}
              />
            </Center>
          </HStack>
        </VStack>

        <GameModal
          header="Game over"
          body={gameOverText}
          isOpen={isOpen}
          onClose={onClose}
        />
      </>
    )
  )
}

export { GameSessionContainer }
