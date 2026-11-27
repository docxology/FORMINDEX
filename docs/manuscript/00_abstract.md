## Abstract

FORMINDEX converts a FORMIS ant-literature export into structured metadata,
selects topic subsets by substring and produces bibliometric visualizations.
We verified the native workflow with the retained July 2024 sample. The
parser returned 317 records, including 198 articles and 85 technical reports.
The topic script returned 580 record-to-topic memberships across 15 nonempty
targets. The target `Art` matched every record because each note contained
“Part of FORMIS,” illustrating how shared metadata can skew topic retrieval.
The native parser, selector and JSON exporters reproduced these findings
offline with the small fixture.
