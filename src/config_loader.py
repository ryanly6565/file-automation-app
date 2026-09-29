import json
from src.actions import *
from src.conditions import *
from src.rules import Rule

def load_rules(file_path: str) -> list[Rule]:
    file_path = Path(file_path)
    if not file_path.exists():
        return []
    
    with open(file_path, 'r') as f:
        rule_data = json.load(f)

    # ensure that there is a rule to follow
    if rule_data.get("rules") == None:
        raise ValueError("Missing required field: rules")
    if not isinstance(rule_data["rules"], list):
        raise ValueError("Type error: rules must be a list")

    # validate rules_list
    rules_list = rule_data["rules"]
    parsed_rules_list = []
    for curr_rule in rules_list:
        if not curr_rule.get("name") or not isinstance(curr_rule.get("name"), str) or curr_rule.get("name") == "":
            raise ValueError("Missing required field: rules must have name")
        rule_name = curr_rule.get("name")
        if not curr_rule.get("watch_folder") or not isinstance(curr_rule.get("watch_folder"), str):
            raise ValueError(f"Missing required field in {rule_name}: rules must watch folders")
        if not curr_rule.get("condition"):
            raise ValueError(f"Missing required field in {rule_name}: rules must have condition")
        if not curr_rule.get("actions") or not isinstance(curr_rule.get("actions"), list):
            raise ValueError(f"Missing required field in {rule_name}: rules must have list of actions")
        enabled = curr_rule.get("enabled", True)
        if not isinstance(enabled, bool):
            raise ValueError("Rule enabled field must be a bool")
        recursive = curr_rule.get("recursive", False)
        if not isinstance(enabled, bool):
            raise ValueError("Recursive field must be a bool")

        condition = make_condition_from_json(curr_rule["condition"], rule_name)
        actions = make_actions_from_json(curr_rule["actions"], rule_name)
        parsed_rules_list.append(Rule(condition=condition, 
                                      actions=actions, 
                                      watch_folder=Path(curr_rule.get("watch_folder")), 
                                      name=curr_rule.get("name"), 
                                      enabled=enabled,
                                      recursive=recursive))

    return parsed_rules_list

def rule_to_json(rule: Rule) -> dict:
    return {
        "name": rule.name,
        "watch_folder": str(rule.watch_folder),
        "condition": condition_to_json(rule.condition),
        "actions": [
            action_to_json(action)
            for action in rule.actions
        ],
        "enabled": rule.enabled,
        "recursive": rule.recursive,
    }

def save_rules(file_path: str, rules: list[Rule]) -> None:
    data = {"rules": [rule_to_json(rule) for rule in rules]}
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

def make_condition_from_json(condition, rule_name):
    if not condition.get("type"):
        raise ValueError(f"In the rule '{rule_name}': Missing required field: conditions must have a type")

    if condition["type"] == "extension":
        if not condition.get("value") or not isinstance(condition["value"], str):
            raise ValueError(f"In the rule '{rule_name}': Extension conditions must have a string extension to match")
        return ExtensionCondition(condition["value"])

    if condition["type"] == "name_contains":
        case_matters = condition.get("case_sensitive", False)
        if case_matters is None or not isinstance(case_matters, bool):
            raise ValueError(f"In the rule '{rule_name}': Case sensitive must be a bool")

        if not condition.get("value") or not isinstance(condition["value"], str):
            raise ValueError(f"In the rule '{rule_name}': Name contains conditions must have a substring to match")
        return NameContainsCondition(condition["value"], condition.get("case_sensitive", False))

    if condition["type"] == "name_starts_with":
        case_matters = condition.get("case_sensitive")
        include_extension = condition.get("include_extension")

        if not condition.get("value") or not isinstance(condition["value"], str):
            raise ValueError(f"In the rule '{rule_name}': Name starts with conditions must have a substring to match")
        
        if case_matters is None or not isinstance(case_matters, bool):
            raise ValueError(f"In the rule '{rule_name}': Case sensitive must be a bool")

        if include_extension is None or not isinstance(include_extension, bool):
            raise ValueError(f"In the rule '{rule_name}': Include extension must be a bool")
        return NameStartsWithCondition(condition["value"], case_matters, include_extension)

    if condition["type"] == "name_ends_with":
        case_matters = condition.get("case_sensitive")
        include_extension = condition.get("include_extension")

        if not condition.get("value") or not isinstance(condition["value"], str):
            raise ValueError(f"In the rule '{rule_name}': Name ends with conditions must have a substring to match")
        
        if case_matters is None or not isinstance(case_matters, bool):
            raise ValueError(f"In the rule '{rule_name}': Case sensitive must be a bool")

        if include_extension is None or not isinstance(include_extension, bool):
            raise ValueError(f"In the rule '{rule_name}': Include extension must be a bool")
        return NameEndsWithCondition(condition["value"], case_matters, include_extension)

    if condition["type"] == "exact_name":
        case_matters = condition.get("case_sensitive")
        include_extension = condition.get("include_extension")

        if not condition.get("value") or not isinstance(condition["value"], str):
            raise ValueError(f"In the rule '{rule_name}': Exact name conditions must have a substring to match")
        
        if case_matters is None or not isinstance(case_matters, bool):
            raise ValueError(f"In the rule '{rule_name}': Case sensitive must be a bool")

        if include_extension is None or not isinstance(include_extension, bool):
            raise ValueError(f"In the rule '{rule_name}': Include extension must be a bool")

        return ExactNameCondition(condition["value"], case_matters, include_extension)

    if condition["type"] == "and":
        if not condition.get("conditions") or not isinstance(condition["conditions"], list):
            raise ValueError(f"In the rule '{rule_name}': And conditions must have a list of conditions")
        return AndCondition([make_condition_from_json(curr_condition, rule_name) for curr_condition in condition["conditions"]])

    if condition["type"] == "or":
        if not condition.get("conditions") or not isinstance(condition["conditions"], list):
            raise ValueError(f"In the rule '{rule_name}': Or conditions must have a list of conditions")
        return OrCondition([make_condition_from_json(curr_condition, rule_name) for curr_condition in condition["conditions"]])

    if condition["type"] == "size":
        size = condition.get("value")
        comparison = condition.get("comparison")

        if size is None or not isinstance(size, int):
            raise ValueError(f"In the rule '{rule_name}': Size conditions must have a size")

        if comparison not in {"gt", "gte", "eq", "lt", "lte"}:
            raise ValueError(f"In the rule '{rule_name}': Size conditions must have a valid comparison")

        return SizeCondition(size=size, comparison=comparison)
    
    raise ValueError(f"In the rule '{rule_name}': Unknown condition type")

def make_actions_from_json(actions, rule_name):
    actions_list = []
    for curr_action in actions:
        if not curr_action.get("type"):
            raise ValueError(f"Missing required field in {rule_name}: actions must have a type")
        
        if curr_action["type"] == "move":
            if not curr_action.get("destination") or not isinstance(curr_action["destination"], str):
                raise ValueError(f"In the rule '{rule_name}': Moving action must have a target destination")
            collision_policy = curr_action.get("collision_policy", "rename")
            actions_list.append(MoveAction(curr_action["destination"], collision_policy=collision_policy))
            continue

        if curr_action["type"] == "copy":
            if not curr_action.get("destination") or not isinstance(curr_action["destination"], str):
                raise ValueError(f"In the rule '{rule_name}': Copying action must have a target destination")
            collision_policy = curr_action.get("collision_policy", "rename")
            actions_list.append(CopyAction(curr_action["destination"], collision_policy=collision_policy))
            continue

        if curr_action["type"] == "prefix_rename":
            if not curr_action.get("value") or not isinstance(curr_action["value"], str):
                raise ValueError(f"In the rule '{rule_name}': Prefix renaming action must have a prefix string")
            actions_list.append(PrefixRenamingAction(curr_action["value"]))
            continue

        if curr_action["type"] == "suffix_rename":
            if not curr_action.get("value") or not isinstance(curr_action["value"], str):
                raise ValueError(f"In the rule '{rule_name}': Suffix renaming action must have a prefix string")
            actions_list.append(SuffixRenamingAction(curr_action["value"]))
            continue

        if curr_action["type"] == "replace_text":
            old_str = curr_action.get("old_str")
            new_str = curr_action.get("new_str")
            first_instance_only = curr_action.get("first_instance_only", True)
            if old_str is None or not isinstance(old_str, str):
                raise ValueError(f"In the rule '{rule_name}': Replace text action must have an old string")
            if new_str is None or not isinstance(new_str, str):
                raise ValueError(f"In the rule '{rule_name}': Replace text action must have a new string")
            if not isinstance(first_instance_only, bool):
                raise ValueError(f"In the rule '{rule_name}': Replace text action's first instance only field must be a bool")
            actions_list.append(ReplaceTextAction(old_str=old_str, new_str=new_str, first_instance_only=first_instance_only))
            continue

        if curr_action["type"] == "change_extension":
            new_ext = curr_action.get("new_ext")
            if new_ext is None or not isinstance(new_ext, str):
                raise ValueError(f"In the rule '{rule_name}': Change extension must have a new extension string.")
            actions_list.append(ChangeExtensionAction(new_ext))
            continue

        if curr_action["type"] == "delete":
            trash_bin = curr_action.get("trash_bin")
            if trash_bin is None or not isinstance(trash_bin, bool):
                raise ValueError(f"In the rule '{rule_name}': Delete action must have a trash_bin bool")
            actions_list.append(DeleteAction(trash_bin))
            continue

        if curr_action["type"] == "compress":
            actions_list.append(CompressAction())
            continue

        if curr_action["type"] == "execute_script":
            if not curr_action.get("source") or not isinstance(curr_action["source"], str):
                raise ValueError(f"In the rule '{rule_name}': Execute script action must have a source script file path")

            kwargs = {
                "source": curr_action.get("source")
            }

            script_type = curr_action.get("script_type")
            if script_type is None or not isinstance(script_type, str):
                raise ValueError(f"In the rule '{rule_name}': Execute script action must have a script_type string")
            kwargs["script_type"] = script_type

            actions_list.append(ExecuteScriptAction(**kwargs))
            continue

        raise ValueError("Unknown action type")
    return actions_list

def condition_to_json(condition: Condition) -> dict:
    if isinstance(condition, ExtensionCondition):
        return {
            "type": "extension",
            "value": condition.extension,
        }

    if isinstance(condition, NameContainsCondition):
        return {
            "type": "name_contains",
            "value": condition.substr,
            "case_sensitive": condition.case_matters,
        }

    if isinstance(condition, SizeCondition):
        return {
            "type": "size",
            "value": condition.size,
            "comparison": condition.comparison,
        }

    if isinstance(condition, NameStartsWithCondition):
        return {
            "type": "name_starts_with",
            "value": condition.substr,
            "case_sensitive": condition.case_matters,
            "include_extension": condition.include_extension
        }

    if isinstance(condition, NameEndsWithCondition):
        return {
            "type": "name_ends_with",
            "value": condition.substr,
            "case_sensitive": condition.case_matters,
            "include_extension": condition.include_extension
        }

    if isinstance(condition, ExactNameCondition):
        return {
            "type": "exact_name",
            "value": condition.match_str,
            "case_sensitive": condition.case_matters,
            "include_extension": condition.include_extension
        }

    if isinstance(condition, AndCondition):
        return {
            "type": "and",
            "conditions": [
                condition_to_json(c)
                for c in condition.conditions
            ]
        }

    if isinstance(condition, OrCondition):
        return {
            "type": "or",
            "conditions": [
                condition_to_json(c)
                for c in condition.conditions
            ]
        }

    raise ValueError(
        f"Unsupported condition type: {type(condition).__name__}"
    )

def action_to_json(action: Action) -> dict:
    if isinstance(action, MoveAction):
        return {
            "type": "move",
            "destination": str(action.dst_directory),
            "collision_policy": action.collision_policy,
        }

    if isinstance(action, CopyAction):
        return {
            "type": "copy",
            "destination": str(action.dst_directory),
            "collision_policy": action.collision_policy,
        }

    if isinstance(action, PrefixRenamingAction):
        return {
            "type": "prefix_rename",
            "value": action.new_prefix,
        }

    if isinstance(action, SuffixRenamingAction):
        return {
            "type": "suffix_rename",
            "value": action.new_suffix,
        }

    if isinstance(action, ReplaceTextAction):
        return {
            "type": "replace_text",
            "old_str": action.old_str,
            "new_str": action.new_str,
            "first_instance_only": action.first_instance_only,
        }

    if isinstance(action, ChangeExtensionAction):
        return {
            "type": "change_extension",
            "new_ext": action.new_ext,
        }

    if isinstance(action, DeleteAction):
        return {
            "type": "delete",
            "trash_bin": action.trash_bin,
        }

    if isinstance(action, CompressAction):
        return {
            "type": "compress",
        }

    if isinstance(action, ExecuteScriptAction):
        return {
            "type": "execute_script",
            "source": str(action.script),
            "script_type": action.script_type,
        }

    raise ValueError(
        f"Unsupported action type: {type(action).__name__}"
    )