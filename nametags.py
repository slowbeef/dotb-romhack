# Return name tags for a given MES file
# This could be smart and parse the OOOOOO.MES file
# but it would also require parsing all the MES files to get
# the nametag pointers. Is that really necessary?
# ...Well... maybe.
#
# But encapsulating it in this function at least lets us change that
# implementation later.

def getNameTags(mesName):
    disk1NameTags = {
        "OPEN_1": ["Cole", "Cooger", "Officer Jack"],
        "OPEN_2": ["Cole", "Cooger", "Officer Jack"],
        "000001": ["Cole", "Cooger", "Sheila"],
        "000002": ["Cole", "Cooger", "Sheila"],
        "000003": ["Cole", "Cooger", "Sheila"],
        "000004": ["Cole", "Cooger", "Sheila"],
        "000005": ["Cole", "Cooger", "Sheila"],
        "000006": ["Cole", "Cooger", "Sheila"],
        "000007": ["Cole", "Cooger", "Sheila"],
        "000008": ["Cole", "Cooger", "Sheila"],
        "000009": ["Cole", "Cooger", "Sheila"],
        "000010": ["Cole", "Cooger", "Sheila"],
        "10PLUS": ["Cole", "Cooger", "Sheila"]
    }
    return disk1NameTags[mesName]
