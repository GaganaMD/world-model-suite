"""Hard identity guard for versioned benchmark references."""
def assert_reference_identity(reference, *, scenario_id, reference_variant, objective_id):
    actual=(reference.get('scenario_id'),reference.get('reference_variant'),reference.get('objective_id'))
    expected=(scenario_id,reference_variant,objective_id)
    if actual != expected:
        raise ValueError(f'reference identity mismatch: expected {expected}, got {actual}')
    return True
