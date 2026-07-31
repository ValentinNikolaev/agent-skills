# Comment Cleanup Examples

Use these examples when a comment is not obviously removable or preservable.

## Remove redundant comments

Remove comments that only repeat what nearby code already says.

```go
// Increment retry count.
retryCount++
```

```typescript
// Return true if user is active.
return user.active === true
```

```python
# Create an empty list.
items = []
```

## Preserve intent and constraints

Keep comments that explain a reason, constraint, or external dependency that is not obvious from the code.

```go
// The billing API rejects events older than 24 hours.
if event.Age() > maxBillingEventAge {
	return nil
}
```

```typescript
// Keep this synchronous; downstream consumers rely on deterministic ordering.
listeners.forEach(listener => listener(event))
```

```python
# The vendor normalizes IDs case-sensitively, despite their docs saying otherwise.
vendor_id = raw_id.lower()
```

## Shorten verbose comments

Preserve useful meaning while removing narration.

Before:

```go
// We sort records by creation time here because the external reporting API
// expects chronological input and otherwise computes cumulative totals wrong.
sort.Slice(records, byCreatedAt)
```

After:

```go
// Reporting totals require chronological records.
sort.Slice(records, byCreatedAt)
```

## Preserve tool-interpreted comments

Do not remove directives unless their semantics are fully understood.

```typescript
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const payload: any = parseLegacyPayload(input)
```

```python
# type: ignore[import-untyped]
import legacy_vendor_sdk
```

```go
//go:build linux
```

## Ambiguous cases

When a comment may encode domain knowledge, preserve it unless surrounding code or documentation proves it is redundant.

```python
# Legacy accounts may not have a region until their first invoice.
region = account.region or default_region
```

When a comment is vague but clearly has no current information value, remove it.

```go
// TODO: fix later
```
