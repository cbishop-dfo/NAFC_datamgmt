from Toolkits import ships_biological
import pandas as pd
if __name__ == '__main__':
    df = ships_biological.createShipDF()
    file = open("NewShips.txt")
    NEWIDS = []
    for d in df.values:
        for line in file:
            if line.lower().__contains__(d[1]):
                newID = line.split()[0]
                row = [d, newID]
                NEWIDS.append(row)
                break
        print(line)