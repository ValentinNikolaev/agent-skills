# Parsing Contracts

This self-contained example targets Zod 4.4.3 and TypeScript 5.9.3 for reproducible verification. It uses Zod 4 APIs and codecs introduced in 4.1; test other supported versions explicitly. Do not replace an existing project's dependency versions to match the example.

```typescript
import { z } from "zod";

export const UserSchema = z.strictObject({
  name: z.string().trim().min(1),
  age: z.coerce.number<string | number>().int().min(18),
  email: z.email(),
  role: z.enum(["member", "admin"]).default("member"),
});
export type UserInput = z.input<typeof UserSchema>;
export type User = z.output<typeof UserSchema>;

export type ParsedUser =
  | { kind: "valid"; data: User }
  | { kind: "invalid-json" }
  | { kind: "invalid-data"; issues: z.core.$ZodIssue[] };

export function parseUserJson(text: string): ParsedUser {
  let value: unknown;
  try {
    value = JSON.parse(text);
  } catch {
    return { kind: "invalid-json" };
  }
  const parsed = UserSchema.safeParse(value);
  if (!parsed.success) return { kind: "invalid-data", issues: parsed.error.issues };
  return { kind: "valid", data: parsed.data };
}

export const DefaultsSchema = z.object({
  name: z.string().default("Anonymous").optional(),
});
export const CountsSchema = z.record(z.string(), z.number().int());
export const UsernameSchema = z.string().refine(
  async (name) => name !== "taken",
  { error: "Username unavailable" },
);
export const DateCodec = z.codec(z.iso.datetime(), z.date(), {
  decode: (iso) => new Date(iso),
  encode: (date) => date.toISOString(),
});
```

Test these independently observed outcomes:

- Malformed JSON returns `invalid-json`; a valid JSON string with the wrong shape returns `invalid-data`.
- A valid user with age `"20"` returns numeric age 20, a trimmed name, and default role `member`. Reject extra fields under this explicit strict-object contract.
- Parsing does not normalize the original input in place. Use the parsed `data`; returning only `success` cannot make a transforming schema a sound output-type predicate over the original object.
- `DefaultsSchema.parse({})` returns `{ name: "Anonymous" }` under this Zod version. `CountsSchema` rejects a string count.
- Await `UsernameSchema.safeParseAsync(...)` and observe both success and validation failure. The example's callback performs no network request; an actual availability lookup also needs an infrastructure-error policy.
- Decode a valid ISO timestamp to a Date and encode it to the expected ISO string. Reject invalid ISO strings and invalid Dates with the relevant safe methods. Normalization may make string round trips differ from their original spelling.

JSON syntax failures and expected schema failures are intentionally separate. Unexpected exceptions from custom callbacks are not silently converted into schema success or a generic invalid-input response.
