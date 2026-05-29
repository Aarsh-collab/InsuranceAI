import copy

def apply_state_updates(state_dict, updates):
    new_state = copy.deepcopy(state_dict)

    for path, value in updates.items():
        keys = path.split(".")
        cursor = new_state

        # Walk down until the parent of the final key
        for key in keys[:-1]:
            if not isinstance(cursor, dict):
                raise ValueError(f"Invalid path segment '{key}' (expected dict, got {type(cursor)})")

            if key not in cursor or cursor[key] is None:
                cursor[key] = {}

            cursor = cursor[key]

        final_key = keys[-1]

        if not isinstance(cursor, dict):
            raise ValueError(f"Cannot assign into non-dict at '{final_key}'")

        # 🔒 Special handling for refused_fields (must always be a dict)
        if final_key == "refused_fields":
            if not isinstance(value, dict):
                raise ValueError("refused_fields must be a dictionary")

            existing = cursor.get(final_key) or {}
            if not isinstance(existing, dict):
                raise ValueError("refused_fields in state must be a dictionary")

            # merge dictionaries (new values override old ones)
            merged = existing.copy()
            merged.update(value)
            cursor[final_key] = merged
        else:
            cursor[final_key] = value

    return new_state