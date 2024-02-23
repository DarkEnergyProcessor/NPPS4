# NPPS4 example Badwords Checker file.
# This defines if a certain words are badwords or not.
# Bad words are words that can't be used in team formation, names, etc.
# You can specify other, vanilla Python file, but it must match the function specification below.
#
# This is free and unencumbered software released into the public domain.
#
# Anyone is free to copy, modify, publish, use, compile, sell, or distribute
# this software, either in source code form or as a compiled binary, for any
# purpose, commercial or non-commercial, and by any means.
#
# In jurisdictions that recognize copyright laws, the author or authors of this
# software dedicate any and all copyright interest in the software to the public
# domain. We make this dedication for the benefit of the public at large and to
# the detriment of our heirs and successors. We intend this dedication to be an
# overt act of relinquishment in perpetuity of all present and future rights to
# this software under copyright law.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# For more information, please refer to <http://unlicense.org/>

import re

import npps4.data
import npps4.idol

STRIP_WHITESPACE = re.compile(r"\s+")


# Badwords Checker must define "has_badwords" function with these parameters:
# * "text" (str)
# * "context" (npps4.idol.BasicSchoolIdolParams) to access the database.
#
# It then returns a boolean if the specified text contains badword.
async def has_badwords(text: str, context: npps4.idol.BasicSchoolIdolContext) -> bool:
    new_text = re.sub(STRIP_WHITESPACE, "", text.lower())
    server_data = npps4.data.get()

    for badword in server_data.badwords:
        if badword in new_text:
            return True

    return False
