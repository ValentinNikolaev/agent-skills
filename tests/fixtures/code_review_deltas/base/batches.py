def batch_count(items, capacity):
    return max(1, (items + capacity - 1) // capacity)
