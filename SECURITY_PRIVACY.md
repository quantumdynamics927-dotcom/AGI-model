# Security & Privacy Guidelines

This document outlines recommended policies for handling `real_data/` (EEG/fMRI) in the repository.

## Data Provenance
- Maintain a `DATA_PROVENANCE.md` record per dataset including source, collection date, and consent details.
- Do not commit raw identifiable data to the repository.

## Consent & Ethical Review
- Ensure all human-subject datasets have documented informed consent and IRB approvals where required.
- Store IRB approvals and consent documentation in a restricted access area outside the public repo.

## Anonymization & Pseudonymization
- Apply irreversible anonymization/pseudonymization to raw EEG/fMRI records before storage.
- Remove direct identifiers and reduce indirect identifiers where possible.

## Access Control
- Restrict access to sensitive data to authorized project members.
- Use encrypted storage and maintain access logs.

## Retention & Deletion
- Define retention periods for datasets and securely delete data no longer needed.

## CI / Testing Practices
- Use synthetic or redacted subsets for CI tests and public artifacts.
- Never expose full real datasets in CI logs or artifacts.

## Local-only operation policy
- By default, the codebase disallows remote uploads and external persistence: upload endpoints are disabled unless the environment variable `TMTOS_ALLOW_UPLOAD='true'` is explicitly set.
- Delivery roots must be local filesystem paths; enforcement is enabled by default via `TMTOS_ENFORCE_LOCAL_PATHS='true'` and the system will raise an error for non-local paths (http/s3/ftp, etc.).
- Do not enable uploads on public, cloud, or untrusted systems unless a security review is completed.

## Contact
For questions about compliance, contact the project data steward and the institutional privacy officer.
