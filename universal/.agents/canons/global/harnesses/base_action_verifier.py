import os
from typing import Tuple, Optional, Any

class BaseActionVerifier:
    """
    Base boilerplate template for creating a custom Action-Verifier.
    Agents should subclass this to implement specific validation constraints
    before proposing actions or executing changes in the environment.
    """

    def __init__(self, action_id: str):
        self.action_id = action_id
        self.is_legal = False
        self.violated_rule: Optional[str] = None
        self.fix_hint: Optional[str] = None

    def verify_action(self, action: Any) -> Tuple[bool, Optional[str]]:
        """
        Main validation function.
        Returns:
            Tuple[bool, Optional[str]]: (is_legal, violated_rule)
        """
        # Override this method in your specific verifier
        raise NotImplementedError("Subclasses must implement verify_action()")

    def log_violation(self, rule_name: str, hint: str):
        """
        Helper method to correctly state the violation and hint.
        """
        self.is_legal = False
        self.violated_rule = rule_name
        self.fix_hint = hint

    def get_report(self) -> dict:
        """
        Generates the standard Harness Output Contract.
        """
        return {
            "action_id": self.action_id,
            "is_legal": self.is_legal,
            "violated_rule": self.violated_rule or "none",
            "fix_hint": self.fix_hint or "none"
        }

if __name__ == "__main__":
    # Example test runner
    verifier = BaseActionVerifier("test_action_001")
    try:
        verifier.verify_action({})
    except NotImplementedError:
        print("Base template loaded correctly. Please implement verify_action().")
