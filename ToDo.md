# FORMIS Database Maintenance and Update Plan

## Overview
Maintaining and updating FORMIS requires the cooperative efforts of myrmecologists worldwide. This document outlines the tasks and areas for improvement to keep FORMIS a valuable resource for the myrmecology community.

## Immediate Actions for Contributors
1. Inspect citations of your own work for accuracy and completeness.
2. Add keywords and/or abstracts to existing entries where possible.

## How to Contribute
Please refer to the next section for detailed instructions on how to contribute or update citations.

## Database Updates
- AGRICOLA will be searched regularly to keep FORMIS updated.
  - Note: This will only find a small portion of the literature.

COMPLETED 
## Specialty Bibliographies Needed
### Genera-specific bibliographies:
- Formica
- Camponotus
- Myrmica
- Pheidole
- Monomorium
- Messor
- Cataglyphis

### Subject-specific bibliographies:
- Foraging
- Bioenergetics
- Myrmecophiles
- Ant-plant symbioses

### Geographic bibliographies:
- Hawaii
- India
- Mexico
- Brazil
- Other regions of interest

### Requirements for specialty bibliographies:
- Can range from a few dozen citations to several thousand
- Must be thorough in their coverage

## Additional Contribution Methods
- Add new citations by journal
- Contact Dr. Porter if interested in adding a bibliography to FORMIS

## User Guidelines
1. Users are welcome to create customized bibliographies from FORMIS.
2. Be aware that personal modifications to FORMIS will be lost in future updates if not sent in for official inclusion.
3. When using EndNote to automatically create bibliographies:
   - Note that citation numbers in FORMIS will not be consistent from year to year.
   - A paper started on one database version should be finished on the same version.

## Future Development Ideas
1. Implement a system for users to submit updates and new entries directly.
2. Develop a web interface for easier browsing and searching of the database.
3. Create an API for programmatic access to FORMIS data.
4. Establish a regular update schedule and announcement system for new versions.
5. Collaborate with other entomological databases for cross-referencing and data sharing.
6. Refine and expand the genus-level bibliography generation script:
   - Improve genus detection accuracy
   - Add options for different output formats (e.g., BibTeX, CSV)
   - Implement a user interface for selecting specific genera

## Recent Updates
- Modified the script (`Scripts/generate_genus_bibliographies.py`) to generate targeted bibliographies for specific genera, subjects, and geographic areas.
- The script now focuses on the following targets:
  - Genera: Formica, Camponotus, Myrmica, Pheidole, Monomorium, Messor, Cataglyphis
  - Subjects: Foraging, Bioenergetics, Myrmecophiles, Ant-plant symbioses
  - Geographic areas: Hawaii, India, Mexico, Brazil

## Contact Information
For inquiries about contributing to FORMIS or adding bibliographies, please contact @docxology on GitHub.