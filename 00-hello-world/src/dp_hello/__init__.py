"""dp-hello: print a greeting to standard output (curriculum project 00-hello-world).

The package is split into one module per responsibility (SRS NFR-04):

* :mod:`dp_hello.options`: command-line parsing (CONV-07 ... CONV-13)
* :mod:`dp_hello.validation`: option-value validation (FR-03, FR-05)
* :mod:`dp_hello.greeting`: pure greeting construction (FR-01, FR-02, FR-04, NFR-05)
* :mod:`dp_hello.output`: byte-exact, LF-only output and diagnostics (CONV-03, CONV-05)
* :mod:`dp_hello.cli`: the entry point that wires them together
"""
