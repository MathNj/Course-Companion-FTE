#!/usr/bin/env python3
"""
Validation script for quiz-master skill.

Checks that all required files and structure are present.
"""

import os
import sys


def validate_skill():
    """Validate the quiz-master skill structure."""
    skill_path = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(skill_path)

    # Check required files
    required_files = [
        os.path.join(parent_dir, "SKILL.md"),
        skill_path,
    ]

    print("Validating quiz-master skill...")

    # Check if SKILL.md exists
    skill_md = os.path.join(parent_dir, "SKILL.md")
    if not os.path.exists(skill_md):
        print(f"[ERROR] SKILL.md not found at {skill_md}")
        return False

    # Read and validate SKILL.md content
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check required frontmatter fields
    required_fields = ['name:', 'description:']
    missing_fields = [field for field in required_fields if field not in content]

    if missing_fields:
        print(f"[ERROR] Missing required frontmatter fields: {missing_fields}")
        return False

    # Check that the skill name is correct
    if 'name: quiz-master' not in content:
        print("[ERROR] Skill name is not 'quiz-master'")
        return False

    # Check that key sections are present
    required_sections = [
        '## Core Philosophy',
        '## Quiz Flow',
        '## Positive Reinforcement Techniques',
        '## Encouragement Language',
        '## Integration with Backend',
    ]

    missing_sections = [section for section in required_sections if section not in content]

    if missing_sections:
        print(f"[WARNING] Missing recommended sections: {missing_sections}")

    # All checks passed
    print("[SUCCESS] quiz-master skill validated successfully!")
    print(f"  - SKILL.md: {skill_md}")
    print(f"  - Name: quiz-master")
    print(f"  - Description: Educational quiz facilitator")
    return True


if __name__ == "__main__":
    success = validate_skill()
    sys.exit(0 if success else 1)
