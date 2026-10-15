# Enforced Type Contracts

This self-contained example targets TypeScript 5.5+ with strict checking and unchecked indexed access enabled. Use the repository's project command; these settings illustrate the fixture rather than prescribe a config migration. TypeScript strips these types at runtime.

```typescript
export type Equal<A, B> =
  (<T>() => T extends A ? 1 : 2) extends
  (<T>() => T extends B ? 1 : 2) ? true : false;
export type Expect<T extends true> = T;

export type ElementOf<T> = T extends readonly (infer Item)[] ? Item : never;
export type TupleElement = Expect<Equal<ElementOf<readonly [1, 2]>, 1 | 2>>;
export type EmptyElement = Expect<Equal<ElementOf<readonly []>, never>>;

// A plain Equal<string, number> alias would merely evaluate to false.
// @ts-expect-error: the enforcing constraint must reject false
export type WrongEquality = Expect<Equal<string, number>>;

export function first<T>(items: readonly T[]): T | undefined {
  return items[0];
}
export const firstNumber = first([1, 2]);
export type FirstResult = Expect<Equal<typeof firstNumber, number | undefined>>;

type Events = { saved: { id: string }; removed: { count: number } };
type EventArgs = { [K in keyof Events]: [event: K, payload: Events[K]] }[keyof Events];
export function describeEvent(...args: EventArgs): string {
  if (args[0] === "saved") return args[1].id;
  return String(args[1].count);
}
describeEvent("saved", { id: "a" });
describeEvent("removed", { count: 2 });
// @ts-expect-error: payload must match the event, not merely some union member
describeEvent("saved", { count: 2 });

export const labels = { saved: "Saved", removed: "Removed" } satisfies Record<keyof Events, string>;
export type KnownKeys = Expect<Equal<keyof typeof labels, "saved" | "removed">>;
```

The equality helper is used only for the concrete types shown; it is not a universal equivalence proof for `any`, overloads, or every recursive type. Keep the accepted calls and negative calls together so a widened API cannot silently erase the intended rejection.

In a disposable copy, remove the two `@ts-expect-error` directives: the equality constraint and mismatched payload must each produce their relevant diagnostic. Restore the directives and require a clean compile. Then change a rejected call to a valid one while retaining its directive: the compiler must reject the unused directive. These controls distinguish an enforced test from comments or aliases that never affect compiler success.
