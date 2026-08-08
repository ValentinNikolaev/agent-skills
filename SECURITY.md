# Security Policy

## Supported Versions

Security fixes are applied to the current `master` branch and included in the
next release. Older releases are not actively supported.

| Version | Supported |
| --- | --- |
| Current `master` and latest release | Yes |
| Older releases | No |

## Reporting a Vulnerability

Do not disclose a suspected vulnerability in a public issue, pull request,
discussion, or social media post.

Use GitHub's private vulnerability reporting from the repository's
[Security advisories page](https://github.com/ValentinNikolaev/llm-skills/security/advisories).
If the **Report a vulnerability** button is unavailable, email
[valeinikolaev@gmail.com](mailto:valeinikolaev@gmail.com) with the subject
`[llm-skills security]`.

Include as much of the following as possible:

- the affected release, commit, skill, or workflow;
- the vulnerability's impact and realistic attack scenario;
- reproduction steps or a minimal proof of concept;
- relevant logs or configuration with secrets removed; and
- any suggested mitigation or fix.

You should receive an acknowledgment within seven days and an initial assessment
within fourteen days. Timelines for a fix and coordinated disclosure depend on
severity and complexity. Please allow a reasonable remediation period before
public disclosure.

## Scope

Relevant reports include vulnerabilities in skill instructions, bundled scripts,
plugin manifests, generators, or GitHub Actions that could cause unintended
command execution, secret exposure, permission-boundary bypass, destructive
behavior, or supply-chain compromise.

General prompt-injection or jailbreak reports should demonstrate a concrete
impact against a documented security boundary. Reports about third-party
platforms should be sent to that platform's security team unless this repository
introduces or materially amplifies the vulnerability.
