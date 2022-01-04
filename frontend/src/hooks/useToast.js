import { useToast as useChakraToast } from '@chakra-ui/react'

function useToast(defaultOptions) {
  const toast = useChakraToast()

  return function (options) {
    toast({ ...defaultOptions, ...options })
  }
}

export { useToast }
