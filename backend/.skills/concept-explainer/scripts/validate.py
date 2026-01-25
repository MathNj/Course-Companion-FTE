#!/usr/bin/env python3
"""Quick validation for concept-explainer skill."""

def validate_skill():
    import os

    skill_path = os.path.dirname(os.path.abspath(__file__))

    # Check SKILL.md exists
    skill_md = os.path.join(skill_path, "..", "SKILL.md")
    if not os.path.exists(skill_md):
        print("Missing SKILL.md")
        return False

    # Check it has required fields
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'name:' not in content:
        print("Missing 'name' field")
        return False

    if 'description:' not in content:
        print("Missing 'description' field")
        return False

    print("concept-explainer skill validated successfully!")
    return True

if __name__ == "__main__":
    import sys
    success = validate_skill()
    sys.exit(0 if success else 1)
