class NUM:
    def __init__(self, at = 0, txt = ""):
        self.at = at
        self.txt = txt
        self.n = 0
        self.mu = 0
        self.m2 = 0
        self.lo = float('inf')
        self.hi = float('-inf') # Replaced sys.maxsize
        self.w = -1 if self.txt.find("-$") != -1 else 1

    def add(self, n):
        """
        Function:
            add
        Description:
            If n is not ?, n on the instance object is incremented by one and NUM attributes are re-calculated
        Input:
            self - current NUM instance
            n - value to add
        Output:
            None
        """
        if n != "?": # Why Question mark
            self.n += 1
            n = float(n)
            d = n - self.mu
            self.mu += d / self.n
            self.m2 += d * (n - self.mu)
            self.lo = min(n, self.lo)
            self.hi = max(n, self.hi)

    def mid(self):
        """
        Function:
            mid
        Description:
            returns mu (mean) of the current instance
        Input:
            self - current NUM instance
        Output:
            mu (mean)
        """
        return self.mu

    def div(self):
        """
        Function:
            div
        Description:
            Determines if there is diversity around the center
        Input:
            self - current NUM instance
        Output:
            True or False
        """
        return (self.m2 < 0 or self.n < 2) and 0 or (self.m2 / (self.n - 1)) ** 0.5

    def norm(self, n):
        """
        Function:
            norm
        Description:
            Normalizes a value
        Input:
            self - current NUM instance
            n - value to normalize
        Output:
            Normalized value
        """
        return n if n == "?" else (float(n) - self.lo) / (self.hi - self.lo + 1 + 10 ** (-32))

    def dist(self, n1, n2):
        """
        Function:
            dist
        Description:
            Finds normalized positive difference between 2 values
        Input:
            self - current NUM instance
            n1 - First value
            n2 - Second value
        Output:
            Normalized + difference between n1 and n2
        """
        if n1 == "?" and n2 == "?":
            return 1
        n1, n2 = self.norm(n1), self.norm(n2)
        if n1 == "?":
            n1 = 1 if n2 < 0.5 else 0
        if n2 == "?":
            n2 = 1 if n1 < 0.5 else 0
        return abs(n1 - n2)
