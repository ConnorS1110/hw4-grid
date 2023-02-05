from num import NUM
from sym import SYM
import re

class COLS:
    def __init__(self, t):
        self.names, self.all, self.x, self.y, self.klass = t, [], [], [], []
        for n, s in enumerate(t):
            if re.match(r"^[A-Z]+", s):
                col = NUM(n, s)
            else:
                col = SYM(n, s)
            self.all.append(col)
            if not re.search(r"X$", s):
                if re.search(r"!$", s):
                    self.klass = col
                if re.search(r"[!+-]$", s):
                    self.y.append(col)
                else:
                    self.x.append(col)

    def add(self, row):
        """
        Function:
            add
        Description:
            adds row data to respective columns
        Input:
            self - current COLS instance
            row - row data to add for each column
        Output:
            None
        """
        for t in [self.x, self.y]:
            for col in t:
                col.add(row.cells[col.at])
