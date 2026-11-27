# Materials and methods

The source was the tracked file
`Initial_Files/FORMIS 2024(July)-Bibtext_316_sample.txt`. We counted its entry
headings after decoding the UTF-8 byte order mark and compared the count with
the records returned by the native parser. The initial report used the
count stated in the filename [@friedman2024oct08].

`load_bibtex` detects the encoding and calls `process_bibtex`. The parser
starts a record on a line beginning with `@`, stores the type under
`ref_type`, lowercases field names and treats lines with an equals sign as
field assignments. Its line-oriented handling makes multiline values and
closing braces worth checking before treating fields as normalized metadata.

`generate_targeted_bibliographies` scans every string field, including the
note and parsed type, for case-insensitive substrings. A set ensures each
record contributes at most one membership to a given target. It can
contribute to multiple targets. We counted nonempty targets, memberships,
and notes containing the literal substring “part of formis.”

The verifier exported the parsed metadata and topic subsets to a temporary
directory, reloaded them through the native JSON loader and compared the
complete data structures. It emitted aggregate counts and plotted the
distribution of record types.
