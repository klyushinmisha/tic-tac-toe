import {
  Alert,
  AlertDescription,
  AlertIcon,
  AlertTitle,
  Button,
  Container,
  FormControl,
  Link,
  Radio,
  Box,
  RadioGroup,
  Stack,
} from '@chakra-ui/react'
import React from 'react'
import { PAGE_URL } from '../config'

function withPreventDefault(f) {
  return function (e, ...args) {
    e.preventDefault()
    f(e, ...args)
  }
}

function withDisable(f, disabled = false) {
  return function (e, ...args) {
    if (disabled) {
      return
    }
    f(e, ...args)
  }
}

function CreateSessionForm({ disabled = false, handleCreate }) {
  const [field, setField] = React.useState('3')

  const handleChange = withDisable(setField, disabled)

  const handleSubmit = withPreventDefault(() => {
    handleCreate({
      field: parseInt(field),
    })
  })

  return (
    <Container centerContent justifyContent="center" height="80vh">
      <form>
        <FormControl>
          <RadioGroup onChange={handleChange} value={field}>
            <Stack direction="row">
              <Radio disabled={disabled} value="3">
                3x3
              </Radio>
              <Radio disabled={disabled} value="4">
                4x4
              </Radio>
              <Radio disabled={disabled} value="5">
                5x5
              </Radio>
            </Stack>
          </RadioGroup>
        </FormControl>
        <Box marginTop="10px">
          <Button type="submit" disabled={disabled} onClick={handleSubmit}>
            Create new game
          </Button>
        </Box>
      </form>
    </Container>
  )
}

function CreatedSessionLink({ sessionId }) {
  const sessionLink = PAGE_URL + '/sessions/' + sessionId

  return (
    <Alert
      status="success"
      variant="subtle"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      textAlign="center"
      height="20vh"
      position="sticky"
    >
      <AlertIcon boxSize="40px" mr={0} />
      <AlertTitle mt={4} mb={1} fontSize="lg">
        Session created
      </AlertTitle>
      <AlertDescription maxWidth="sm">
        Send this link to second player:{' '}
        <Link href={sessionLink}>{sessionLink}</Link>
      </AlertDescription>
    </Alert>
  )
}

export { CreateSessionForm, CreatedSessionLink }
