/*
 * Internal CPython logic and datastructures are reused, both in using ast.c
 * and in this file for the purposes of evaluationg fstrings in the interpreter
 * at run time.
 * Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010,
 * 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020 Python Software
 * Foundation; All Rights Reserved
 */
#include "ast.c"

static PyObject *
FYeah_FString(PyObject *self, PyObject *args)
{
    size_t len;
    const char *str_filename = "<fstring>";
    const char *fstring;
    PyArena *arena = NULL;
    node *n = NULL;
    expr_ty fexpr;
    mod_ty fmod;
    PyCodeObject *fcode;
    PyObject *g, *l, *obj_filename;
    PyObject *fevald = NULL;

    obj_filename = PyUnicode_DecodeFSDefault(str_filename);
    if (obj_filename == NULL)
        return NULL;

    if (!PyArg_ParseTuple(args, "s", &fstring))
        goto done;
    len = strlen(fstring);
    if (len > INT_MAX) {
        PyErr_SetString(PyExc_OverflowError, "string to parse is too long");
        goto done;
    }

    // TODO: allocate arena once per import?
    arena = PyArena_New();

    struct compiling c;
    c.c_arena = arena;
    c.c_filename = obj_filename;
    c.c_normalize = NULL;

    n = PyNode_New(eval_input);
    if (n == NULL) {
        goto done;
    }

    // rawmode=0; raw strings will have already been parsed in the python layer
    // recursive=0;
    fexpr = fstring_parse(&fstring, fstring+len, 0, 0, &c, n);
    if (!fexpr) {
        return NULL;
    }

    fmod = (mod_ty)PyArena_Malloc(arena, sizeof(*fmod));
    if (!fmod)
        return NULL;
    fmod->kind = Expression_kind;
    fmod->v.Expression.body = fexpr;

    fcode = PyAST_Compile(fmod, str_filename, NULL, arena);
    if (fcode == NULL)
        return NULL;

    /* namespaces collected as in builtin_eval_impl */
    g = PyEval_GetGlobals();
    l = PyEval_GetLocals();
    if (!g || !l) {
        PyErr_SetString(PyExc_SystemError,
                        "globals and locals cannot be NULL");
        return NULL;
    }

    fevald = PyEval_EvalCode((PyObject*)fcode, g, l);

done:
    Py_XDECREF(obj_filename);
    if (arena != NULL){
        PyArena_Free(arena);
    }
    // NULL check done within
    PyNode_Free(n);
    // if PyEval_EvalCode was not successful, this will return NULL
    return fevald;
}

static PyMethodDef FYeahMethods[] = {
    {"f",  FYeah_FString, METH_VARARGS,
     "Direct eval of only fstrings."},
};

static struct PyModuleDef _cfyeah = {
    PyModuleDef_HEAD_INIT,
    "fyeah",               /* module name */
    "Reusable f-strings",  /* module documentation */
    -1,                    /* size of per-interpreter state of the module,
                              or -1 if the module keeps state in global
                              variables. */
    FYeahMethods
};

PyMODINIT_FUNC
PyInit__cfyeah(void)
{
    return PyModule_Create(&_cfyeah);
}
