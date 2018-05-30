from subprocess import call


def callmethod(stack, dryrun=True):
  print('SYS CALL: '+' '.join(stack))
  if not dryrun:
    return call(stack)
  return 0
