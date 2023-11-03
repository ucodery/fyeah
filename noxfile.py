import nox

@nox.session(python=['3.11'])
def unittest(session):
    session.install('.')
    session.install('pytest')
    session.run('pytest')
