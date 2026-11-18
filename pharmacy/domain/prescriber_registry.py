"""Role A: simulated prescriber allow-list. Fictional codes only."""


class PrescriberRegistry:
    def __init__(self, allowed_codes):
        # TODO: keep the codes in a set
        raise NotImplementedError

    def is_allowed(self, code) -> bool:
        """TODO: membership test. A non-empty string alone is NOT enough."""
        raise NotImplementedError
