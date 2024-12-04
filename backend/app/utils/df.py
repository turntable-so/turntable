def get_first_n_values(n=1):
    def helper(x):
        out = []
        n_added = 0
        for i, v in enumerate(x):
            if v != "" and v != [] and v != {} and v is not None:
                out.append(v)
                n_added += 1
            if n_added == n:
                return out, n_added
        if n_added == 0:
            return [], 0
        return out, n_added

    return helper


def truncate_values(characters: int = 100):
    def helper(val):
        if isinstance(val, str) and len(val) > characters:
            return val[: (characters - 3)] + "..."
        return val

    return helper
