# Comment Cleanup Examples

Use these examples when the correct treatment of a comment is unclear.

The examples illustrate intent. Apply repository and language conventions before copying any pattern.

## Obvious narration

### Go

Before:

```go
// Increment the counter.
counter++

// Return the result.
return result
```

After:

```go
counter++
return result
```

Before:

```go
// Check if the error is not nil.
if err != nil {
	return err
}
```

After:

```go
if err != nil {
	return err
}
```

## Redundant initialization comments

### Python

Before:

```python
# Initialize an empty list.
results = []
```

After:

```python
results = []
```

### TypeScript

Before:

```typescript
// Create a new user.
const user = new User();
```

After:

```typescript
const user = new User();
```

### PHP

Before:

```php
// Loop through all items.
foreach ($items as $item) {
    process($item);
}
```

After:

```php
foreach ($items as $item) {
    process($item);
}
```

## Redundant function documentation

Before:

```go
// GetUser gets a user by ID.
func GetUser(id string) (*User, error) {
	return repository.Find(id)
}
```

When exported documentation is not required:

```go
func GetUser(id string) (*User, error) {
	return repository.Find(id)
}
```

When exported documentation is required and non-obvious behavior exists:

```go
// GetUser returns ErrUserNotFound when no active user has the given ID.
func GetUser(id string) (*User, error) {
	return repository.Find(id)
}
```

Do not invent the error behavior merely to retain a comment.

## Redundant constant documentation

Before:

```go
// DefaultTimeout is the default timeout.
const DefaultTimeout = 30 * time.Second
```

After:

```go
const DefaultTimeout = 30 * time.Second
```

When the value reflects an external constraint:

```go
// DefaultTimeout matches the gateway's maximum request duration.
const DefaultTimeout = 30 * time.Second
```

## Comments describing transformations

Before:

```go
// Convert the string to lowercase.
normalized := strings.ToLower(value)

// Remove whitespace.
normalized = strings.TrimSpace(normalized)
```

After:

```go
normalized := strings.ToLower(value)
normalized = strings.TrimSpace(normalized)
```

## Preserve external behavior

Preserve:

```go
// The provider retries webhooks, so the payment may already exist.
```

The local code may check for an existing payment, but the comment explains why duplicate delivery is expected.

## Replace implementation narration with rationale

Before:

```go
// Sleep for 100 milliseconds.
time.Sleep(100 * time.Millisecond)
```

When the delay has no non-obvious documented reason:

```go
time.Sleep(100 * time.Millisecond)
```

When an external constraint exists:

```go
// The upstream API rejects retries within the same 100 ms window.
time.Sleep(100 * time.Millisecond)
```

## Shorten verbose rationale

Before:

```go
// We need to sort the records by creation time here because the external
// reporting API expects all records to be sent in chronological order,
// otherwise the API can produce incorrect cumulative totals in its reports.
sort.Slice(records, lessByCreatedAt)
```

After:

```go
// Reporting totals require records in chronological order.
sort.Slice(records, lessByCreatedAt)
```

## Preserve operation ordering

Preserve:

```go
// Delete children first because this database does not enforce cascading deletes.
```

The code shows the order, but not why changing the order would be unsafe.

## Preserve retry and idempotency context

Preserve:

```go
// Mark the request complete only after publishing succeeds; the worker may retry.
```

Do not replace it with:

```go
// Publish the event and mark the request complete.
```

The replacement narrates the code and removes the important retry invariant.

## Preserve security constraints

Preserve:

```go
// Compare hashes in constant time to avoid leaking signature information.
```

Do not shorten it to:

```go
// Compare hashes.
```

## Preserve compatibility workarounds

Preserve:

```typescript
// Safari 15 reports zero height until the next animation frame.
requestAnimationFrame(measure);
```

A possible shorter version is:

```typescript
// Safari 15 reports zero height before the next animation frame.
requestAnimationFrame(measure);
```

## Preserve concurrency assumptions

Preserve:

```go
// Only the lease holder may update this record.
```

Do not remove it merely because the surrounding condition checks a lease identifier.

## Decorative sections

Before:

```go
// Validate
if err := validate(input); err != nil {
	return err
}

// Process
result := process(input)

// Return result
return result
```

After:

```go
if err := validate(input); err != nil {
	return err
}

result := process(input)
return result
```

Keep section comments in long files only when they materially improve navigation and match repository conventions.

## Tooling directives

Preserve without rewriting:

```go
//go:build linux
```

```go
//go:generate mockgen -source=client.go
```

```typescript
// eslint-disable-next-line @typescript-eslint/no-explicit-any
```

```python
# type: ignore[arg-type]
```

```php
/** @phpstan-ignore-next-line */
```

Do not convert tool directives into prose.

## TODO markers

Preserve:

```go
// TODO: Remove legacy parsing after mobile clients below v4 are unsupported.
```

Remove when clearly valueless:

```go
// TODO: Improve this.
```

Do not turn it into a fabricated task such as:

```go
// TODO(PROJ-123): Replace this with the new parser by Q4.
```

unless those details already exist in the repository.

## Commented-out code

Before:

```go
// oldClient.Send(request)
newClient.Send(request)
```

After, when the old line is clearly obsolete:

```go
newClient.Send(request)
```

Preserve commented-out code when it belongs to a fixture or intentionally documented example:

```go
// Use insecureTransport only in local integration tests.
// client := NewClient(insecureTransport)
```

## Mixed useful and redundant content

Before:

```go
// Check whether the payment already exists because the payment provider
// retries webhook requests multiple times whenever it does not receive a
// successful HTTP response from our endpoint.
if repository.Exists(paymentID) {
	return nil
}
```

After:

```go
// Provider retries can deliver the same payment more than once.
if repository.Exists(paymentID) {
	return nil
}
```

## Final classification check

Before editing a comment, determine whether it primarily describes:

* **what the next line does** — usually remove;
* **why the code must behave this way** — usually preserve;
* **a useful constraint in too many words** — shorten;
* **tool metadata or a directive** — preserve;
* **unknown domain or tooling behavior** — preserve and report if material.
