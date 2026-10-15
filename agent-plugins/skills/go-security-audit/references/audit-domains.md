# Go Audit Domains

Apply only domains reached by the named attack surface. A pattern match is a candidate to investigate, not a finding or a preset severity.

## Identity and data isolation

- Trace authenticated identity to the authorization decision and the data access. Check object-level and tenant-level access on reads, writes, background jobs, and cache keys; do not assume a trusted internal transport grants every caller authority.
- Check token signature/algorithm constraints and required claims against the actual token contract. Trace session fixation, cookie scope, expiration/revocation, and CSRF defenses for the application's authentication model.
- Confirm secrets and sensitive values are absent from responses, errors, logs, traces, and metric labels. Do not reproduce a secret in the report.

## Injection and outbound requests

- Trace untrusted input into SQL, commands, templates, and generated queries. Check parameterization and dialect, argument boundaries, template context, and validation already performed.
- `html/template` performs contextual HTML escaping; `text/template` does not. Inspect explicit trusted-HTML types and unsafe conversions that can bypass escaping. Trusted template source and untrusted template data are different boundaries.
- For SSRF, inspect allowed schemes, parsed destinations, redirects, name resolution, connection targets, and relevant deployment egress controls. A URL string allowlist alone may not constrain the destination actually dialed.
- For uploads and archives, trace resolved targets, symlinks, overwrite policy, decompressed size/count limits, and cleanup. Lexical normalization alone does not establish filesystem confinement. Check version-supported rooted filesystem APIs or equivalent verified controls.

## Cryptography and transport

- Identify the security property needed: unpredictability, confidentiality, integrity, or password verification. Check algorithm, randomness source, nonce handling, authentication, key ownership/rotation, and error handling against that property.
- Use vetted cryptographic libraries and current primary guidance. Do not declare all uses of a hash or cipher mode vulnerable by name; demonstrate the threatened property and reachable use.
- Check TLS verification, proxy trust, and forwarding headers against actual deployment. Missing browser headers or binding to all interfaces is context-dependent, not automatically an exploitable defect.

## Availability, concurrency, and lifecycle

- Trace untrusted input into allocation, body reads, decompression, expensive computation, regex, database work, and goroutine fan-out. Establish realistic bounds and cancellation/shutdown behavior.
- Check shared state, ownership transfer, and synchronization on security-sensitive decisions. Distinguish an observed race, a statically supported race path, and a suspected interleaving.
- Inspect server/client timeouts against streaming and deployment needs rather than imposing fixed values. Confirm partial failures cannot acknowledge an incomplete authorization or persistence operation as success.

## Dependency and tool evidence

- Match an advisory to the exact resolved module/version, build conditions, and affected symbols. Distinguish package presence from reachable vulnerable behavior; do not dismiss a relevant advisory merely because reachability could not be established.
- Keep module-cache integrity checks, vulnerability advisories, and exploitability analysis distinct. `go.sum` checksums do not prove a dependency trustworthy.
- Separate scanner findings from confirmed audit findings and record missing tools or untested configurations. Never claim a green scan covers excluded packages or deployment-only paths.

Adapted from selected security references in [samber/cc-skills-golang](https://github.com/samber/cc-skills-golang/tree/8e899e20ff0cd4dc524af3993e4c62d8ee8c5717/skills/golang-security/references), under the parent package's scoped MIT license. Verify evolving API/tool facts against the project's supported versions and current official documentation.
