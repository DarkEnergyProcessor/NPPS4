# NPPS4 example Badwords Checker file.
# This defines if a certain words are badwords or not.
# Bad words are words that can't be used in team formation, names, etc.
# You can specify other, vanilla Python file, but it must match
# the function specification below.


# Badwords Checker must define "has_badwords" function with these parameters:
# * "text" (str)
# * "context" (npps4.idol.BasicSchoolIdolParams) to access the database.
#
# It then returns a boolean if the specified text contains badword.
async def has_badwords(text: str, context) -> bool:
    return False
