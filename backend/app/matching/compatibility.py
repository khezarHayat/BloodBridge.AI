"""
Blood group compatibility rules.

Provides a compatibility map that defines which donor blood groups
can donate to which recipient blood groups, along with helper functions.
"""

from typing import Dict, List

# Maps recipient blood group -> list of compatible donor blood groups
COMPATIBILITY_MAP: Dict[str, List[str]] = {
    "A+": ["A+", "A-", "O+", "O-"],
    "A-": ["A-", "O-"],
    "B+": ["B+", "B-", "O+", "O-"],
    "B-": ["B-", "O-"],
    "AB+": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
    "AB-": ["A-", "B-", "AB-", "O-"],
    "O+": ["O+", "O-"],
    "O-": ["O-"],
}

# All valid blood groups
ALL_BLOOD_GROUPS: List[str] = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]

# Blood group display info
BLOOD_GROUP_INFO: Dict[str, Dict[str, object]] = {
    "A+": {
        "name": "A Positive",
        "can_donate_to": ["A+", "AB+"],
        "can_receive_from": ["A+", "A-", "O+", "O-"],
        "population_percentage": 30.9,
    },
    "A-": {
        "name": "A Negative",
        "can_donate_to": ["A+", "A-", "AB+", "AB-"],
        "can_receive_from": ["A-", "O-"],
        "population_percentage": 6.3,
    },
    "B+": {
        "name": "B Positive",
        "can_donate_to": ["B+", "AB+"],
        "can_receive_from": ["B+", "B-", "O+", "O-"],
        "population_percentage": 21.8,
    },
    "B-": {
        "name": "B Negative",
        "can_donate_to": ["B+", "B-", "AB+", "AB-"],
        "can_receive_from": ["B-", "O-"],
        "population_percentage": 1.7,
    },
    "AB+": {
        "name": "AB Positive",
        "can_donate_to": ["AB+"],
        "can_receive_from": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
        "population_percentage": 5.1,
    },
    "AB-": {
        "name": "AB Negative",
        "can_donate_to": ["AB+", "AB-"],
        "can_receive_from": ["A-", "B-", "AB-", "O-"],
        "population_percentage": 0.5,
    },
    "O+": {
        "name": "O Positive",
        "can_donate_to": ["O+", "A+", "B+", "AB+"],
        "can_receive_from": ["O+", "O-"],
        "population_percentage": 28.3,
    },
    "O-": {
        "name": "O Negative (Universal Donor)",
        "can_donate_to": ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"],
        "can_receive_from": ["O-"],
        "population_percentage": 5.4,
    },
}


def is_compatible(donor_group: str, recipient_group: str) -> bool:
    """
    Check if a donor blood group is compatible with a recipient blood group.

    Args:
        donor_group: The donor's blood group (e.g., 'O-').
        recipient_group: The recipient's blood group (e.g., 'A+').

    Returns:
        True if the donor can donate to the recipient, False otherwise.
    """
    compatible_donors = COMPATIBILITY_MAP.get(recipient_group, [])
    return donor_group in compatible_donors


def get_compatible_donor_groups(recipient_group: str) -> List[str]:
    """
    Get the list of donor blood groups compatible with a recipient.

    Args:
        recipient_group: The recipient's blood group.

    Returns:
        List of blood group strings that can donate to this recipient.
        Returns an empty list if the recipient group is unknown.
    """
    return COMPATIBILITY_MAP.get(recipient_group, [])


def is_exact_match(donor_group: str, recipient_group: str) -> bool:
    """
    Check if donor and recipient have the exact same blood group.

    Args:
        donor_group: The donor's blood group.
        recipient_group: The recipient's blood group.

    Returns:
        True if blood groups are identical.
    """
    return donor_group == recipient_group
