class Flags:
    def __init__(self):
        self.neg = 0
        self.zero = 0
        self.carry = 0
        self.overflow = 0

    def reset(self):
        self.neg = self.zero = self.carry = self.overflow = 0

    def set_flags(self, flags_dict):
        self.zero = 1 if flags_dict.get('zero') else 0
        self.neg = 1 if flags_dict.get('negative') else 0
        self.carry = 1 if flags_dict.get('carry') else 0
        self.overflow = 1 if flags_dict.get('overflow') else 0
