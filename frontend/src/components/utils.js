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

export { withPreventDefault, withDisable }
