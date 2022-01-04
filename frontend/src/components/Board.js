import { MoonIcon, StarIcon } from '@chakra-ui/icons'
import { Box, Center, HStack, VStack } from '@chakra-ui/react'
import React from 'react'

function cellFactory(type, props) {
  switch (type) {
    case 'x':
      return <StarIcon {...props} />
    case 'o':
      return <MoonIcon {...props} />
    default:
      return <></>
  }
}

function Board({ state, move, disabled = false }) {
  const handleClick = (i, j) => {
    if (disabled) {
      return
    }
    move(i, j)
  }

  return (
    <VStack spacing={4} align="stretch">
      {state.map((row, i) => (
        <HStack key={i} spacing="24px">
          {row.map((cell, j) => (
            <Center
              onClick={() => handleClick(i, j)}
              key={j}
              w="10vw"
              h="10vw"
              bg="gray.50"
              color="gold"
            >
              <Box
                alignContent="center"
                justifyContent="center"
                as="span"
                fontWeight="bold"
                fontSize="5vw"
              >
                {cellFactory(cell)}
              </Box>
            </Center>
          ))}
        </HStack>
      ))}
    </VStack>
  )
}

export { Board }
