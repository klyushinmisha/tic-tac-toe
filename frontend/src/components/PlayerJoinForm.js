import { Box, Button, Container, Flex, Input } from '@chakra-ui/react'
import React, { useState } from 'react'

function PlayerJoinForm({ handleJoin }) {
  const [player, setPlayer] = useState('')

  const handleInput = (e) => setPlayer(e.target.value)
  const handleJoinSubmit = (e) => {
    e.preventDefault()
    handleJoin(player)
  }

  return (
    <Container centerContent justifyContent="center" height="100vh">
      <form>
        <Input
          value={player}
          onChange={handleInput}
          placeholder="Introduce yourself!"
        />
        <Flex direction="row-reverse">
          <Box paddingTop="10px">
            <Button type="submit" onClick={handleJoinSubmit}>
              Join
            </Button>
          </Box>
        </Flex>
      </form>
    </Container>
  )
}

export { PlayerJoinForm }
