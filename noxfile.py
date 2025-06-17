import nox


@nox.session(python=['3.13'])
def unittest(session):
    session.install('.')
    session.install('pytest')
    session.run('pytest', *session.posargs)


@nox.session
def format(session):
    session.install('ruff')
    session.run('ruff', 'format', '.')
    session.run('ruff', 'check', '.')
