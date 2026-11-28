This one-file change follows a review that found an empty export allocated a batch. The proposed revision is intended to fix that finding. The attached diff is the whole round from the previously reviewed version. No mutation or test results are claimed.

The export planner returns the number of batches needed to carry all items. Items are a nonnegative integer and each batch can carry up to capacity items, where capacity is a positive integer. An empty export allocates zero batches. No other consumers, tests or policy files are included in this snapshot.
