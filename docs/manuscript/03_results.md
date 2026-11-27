# Results

The retained file contains 317 entry headings after decoding its initial
byte order mark. The parser returned 317 records and the JSON round trip
retained each record and each nonempty topic set.

![Parsed record types in the FORMIS sample. Articles number 198, technical reports 85, collection chapters 28, doctoral theses 4 and books 2.](../../output/figures/formis-sample-types.png)

The 15 nonempty targets account for 580 memberships. The `Art` target
accounts for 317 memberships. Every parsed note includes “Part of FORMIS,”
which contains “art.” The result measures the selection rule's response to
common database boilerplate. The same rule returned 47 memberships for
`Foraging`, a count that likewise describes literal matches.

| Sample check | Measured count |
|:---|---:|
| Decoded entry headings | 317 |
| Parsed records | 317 |
| Configured terms | 23 |
| Nonempty topic files | 15 |
| Record-to-topic memberships | 580 |
| Records matching Art | 317 |
| Records with Part of FORMIS in the note | 317 |
