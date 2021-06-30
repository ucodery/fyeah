try:
    from ._cfyeah import f

    # does nothing, but keeps API consistent
    # _cfyeah(str) is still faster than _fyeah(CompiledFstring)
    compile = lambda f: f
except ImportError:
    from ._fyeah import f, compile
