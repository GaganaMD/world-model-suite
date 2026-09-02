"""External, scenario-level feature contracts for symbolic Physical-AI cases."""
from __future__ import annotations
from typing import Any, Mapping

SCHEMAS={
 'P1': {'required':{'location':str,'door_open':bool,'goal_reached':bool},'domains':{'location':{'left','right','goal'}}},
 'P2': {'required':{'robot_location':str,'object_location':str,'carrying':bool,'broken':bool,'delivered':bool},'domains':{}},
 'P3': {'required':{'location':str,'battery':int,'package_delivered':bool,'failed':bool},'domains':{}},
 'P4': {'required':{'location':str,'goal_reached':bool,'collision':bool},'domains':{'location':{'route','goal','collision'}}},
 'P5': {'required':{'location':str,'switch_pressed':bool,'access_open':bool,'goal_reached':bool},'domains':{}}
}

def validate_features(case: str, features: Mapping[str, Any]) -> list[str]:
    schema=SCHEMAS[case]; errors=[]
    for key,typ in schema['required'].items():
        if key not in features: errors.append(f'missing feature {key}'); continue
        if not isinstance(features[key],typ) or (typ is int and isinstance(features[key],bool)): errors.append(f'{key} must be {typ.__name__}')
    for key,allowed in schema['domains'].items():
        if key in features and features[key] not in allowed: errors.append(f'{key} outside allowed domain')
    return errors

def external_predicates(case: str, features: Mapping[str, Any]) -> dict[str,bool]:
    validate=validate_features(case,features)
    if validate: raise ValueError('; '.join(validate))
    if case=='P4': return {'success':features['goal_reached'],'unsafe':features['collision'],'failure':features['collision']}
    if case=='P1': return {'success':features['goal_reached'],'unsafe':False,'failure':False}
    if case=='P2': return {'success':features['delivered'] and not features['broken'],'unsafe':features['broken'],'failure':features['broken']}
    if case=='P3': return {'success':features['package_delivered'],'unsafe':features['failed'],'failure':features['failed']}
    return {'success':features['goal_reached'],'unsafe':False,'failure':False}

def check_instance_features(case: str, instance: Any, states: list[Any]) -> dict[str,Any]:
    errors=[]; checked=0
    for state in states:
        try: features=instance.state_features(state)
        except Exception as e: errors.append(f'{state!r}: state_features failed: {e}'); continue
        if not isinstance(features,Mapping): errors.append(f'{state!r}: features must be a mapping'); continue
        errors.extend(f'{state!r}: {e}' for e in validate_features(case,features)); checked+=1
    return {'state_features_present':checked==len(states),'state_features_schema_valid':not errors,'all_reachable_states_evaluable':not errors,'external_predicates_evaluable':not errors,'states_checked':checked,'errors':errors}
