# Next.js review checks

## Request framing in server-side fetch

Apply this check when a diff adds an outbound call through Next.js's patched server-side `fetch` and the receiving service enforces `Content-Length`, `Transfer-Encoding`, a body signature or hash, or a body-size limit. Establish which runtime executes the call, including calls made through a shared helper.

- Trace the request through the installed Next.js version. In 15.5.0, when the patch rebuilds a `Request` input and the original body value is unavailable, it uses the body stream. If the transport no longer knows the length, it can send the request chunked over HTTP/1.1. Identify which branch the changed call takes and which server check depends on the result. [Next.js request reconstruction](https://github.com/vercel/next.js/blob/v15.5.0/packages/next/src/server/lib/patch-fetch.ts#L712-L736)
- Compare earlier signed calls to the same service. If they were all bodyless and this is the first signed call with a body, say so explicitly and name the existing server-side body check those calls could never reach.
- Require either a wire-level capture of the changed call or a test that exercises the call with the actual Next.js fetch patch active. Check the headers or body bytes the receiver validates, or assert the outcome of running its guard.
- A mocked `fetch` sees the request before Next.js transforms it. If the mock is the only evidence on this path, report a **P2 finding** on the new call. Name the guard, the possible rejection, and the observation that would confirm it.
