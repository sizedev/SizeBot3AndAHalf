import discord
from discord.ext import commands
import re
import datetime
from datetime import *
import time
from time import strftime, localtime
import sys
import os
import math
from math import *
import random
from decimal import *
from colored import fore, back, style, fg, bg, attr
from pathlib import Path
import string
import traceback
import asyncio
import codecs
import digilogger as logger


# TODO: Make this do something useful.
class DigiException(Exception):
    pass


# Version.
version = "3.3.7"

# Defaults
defaultheight = Decimal("1754000")  # micrometers
defaultweight = Decimal("66760000")  # milligrams
defaultdensity = Decimal("1.0")

# Constants
newline = "\n"
folder = ".."
reol = 106871675617820672
sizebot_id = 344590087679639556
digiid = 271803699095928832
yukioid = 140162671445147648
mee6id = 553792568824037386
sizebotuser_roleid = 562356758522101769
brackets = ["[", "]", "<", ">"]
allowbrackets = ("&compare", "&stats")

# Array item names.
NICK = 0
DISP = 1
CHEI = 2
BHEI = 3
BWEI = 4
DENS = 5
UNIT = 6
SPEC = 7


def regenhexcode():
    # 16-char hex string gen for unregister.
    hexdigits = "1234567890abcdef"
    lst = [random.choice(hexdigits) for n in len(hexdigits)]
    hexstring = "".join(lst)
    with open("../hexstring.txt", "w") as hexfile:
        hexfile.write(hexstring)


def readhexcode():
    # Read the hexcode from the file.
    with open("../hexstring.txt", "r") as hexfile:
        hexcode = hexfile.readlines()
    return str(hexcode[0])


# ASCII art.
ascii = r"""
. _____ _        ______       _   _____ .
./  ___(_)       | ___ \     | | |____ |.
.\ `--. _ _______| |_/ / ___ | |_    / /.
. `--. \ |_  / _ \ ___ \/ _ \| __|   \ \.
./\__/ / |/ /  __/ |_/ / (_) | |_.___/ /.
.\____/|_/___\___\____/ \___/ \__\____/ ."""

# Configure decimal module.
getcontext()
context = Context(prec=250, rounding=ROUND_HALF_EVEN, Emin=-9999999, Emax=999999,
                  capitals=1, clamp=0, flags=[], traps=[Overflow, DivisionByZero,
                                                        InvalidOperation])
setcontext(context)


# Get number from string.
def getnum(string):
    match = re.search(r"\d+\.?\d*", string)
    if match is None:
        return None
    return Decimal(match.group(0))


# Get letters from string.
def getlet(string):
    match = re.search(r"[a-zA-Z\'\"]+", string)
    if match is None:
        return None
    return match.group(0)


# Remove trailing zeroes from a Decimal
def trimzeroes(d):
    return d.normalize() + 0


def removebrackets(string):
    for bracket in brackets:
        string = string.replace(bracket, "")
    return string


def round_nearest_half(number):
    return round(number * 2) / 2


def place_value(number):
    return f"{number:,}"


def pretty_time_delta(seconds):
    seconds = int(seconds)
    years, seconds = divmod(seconds, 86400 * 365)
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    if years > 0:
        return '%d years, %d days, %d hours, %d minutes, %d seconds' % (years, days, hours, minutes, seconds)
    elif days > 0:
        return '%d days, %d hours, %d minutes, %d seconds' % (days, hours, minutes, seconds)
    elif hours > 0:
        return '%d hours, %d minutes, %d seconds' % (hours, minutes, seconds)
    elif minutes > 0:
        return '%d minutes, %d seconds' % (minutes, seconds)
    else:
        return '%d seconds' % (seconds)


# Update users nicknames to include sizetags.
async def nickupdate(user):
    if user.discriminator == "0000":
        return
    if not isinstance(user, discord.Member):
        if user.id == mee6id:
            return
        logger.warn(f"Attempted to update user {user.id} ({user.name}), but they DM'd SizeBot.")
    # Don't update owner's nick, permissions error.
    if user.id == user.guild.owner.id:
        # logger.warn(f"Attempted to update user {user.id} ({user.name}), but they own this server.")
        return
    # Don't update users who aren't registered.
    if not os.path.exists(f"{folder}/users/{user.id}.txt"):
        return

    userarray = read_user(user.id)

    # User's display setting is N. No sizetag.
    if userarray[DISP].strip() != "Y":
        return

    height = userarray[CHEI]
    if height is None:
        height = userarray[BHEI]
    nick = userarray[NICK].strip()
    species = userarray[SPEC].strip()

    unit_system = userarray[UNIT].strip().upper()
    if unit_system == "M":
        sizetag = fromSV(height)
    elif unit_system == "U":
        sizetag = fromSVUSA(height)
    else:
        sizetag = ""

    if species != "None":
        sizetag = f"{sizetag}, {species}"

    max_nick_len = 32

    if len(nick) > max_nick_len:
        # User has set their nick too large. Truncate.
        nick = nick[:max_nick_len]

    if len(nick) + len(sizetag) + 3 <= max_nick_len:
        # Fit full nick and sizetag.
        newnick = f"{nick} [{sizetag}]"
    elif len(sizetag) + 7 <= max_nick_len:
        # Fit short nick and sizetag.
        chars_left = max_nick_len - len(sizetag) - 4
        short_nick = nick[:chars_left]
        newnick = f"{short_nick}… [{sizetag}]"
    else:
        # Cannot fit the new sizetag.
        newnick = nick
    try:
        await user.edit(nick=newnick)
    except discord.Forbidden:
        logger.crit(f"Tried to nickupdate {user.id} ({user.name}), but it is forbidden!")
        return

    #logger.msg(f"Updated user {user.id} ({user.name}).")


# Read in specific user.
def read_user(user_id):
    user_id = str(user_id)
    userfile = folder + "/users/" + user_id + ".txt"
    with open(userfile) as f:
        # Make array of lines from file.
        content = f.readlines()
        if content == []:
            os.remove(userfile)
        # Replace None.
        if content[BWEI] == "None" + newline:
            content[BWEI] = str(defaultweight) + newline
        if content[BHEI] == "None" + newline:
            content[BHEI] = str(defaultweight) + newline
        if content[CHEI] == "None" + newline:
            content[CHEI] = content[3]
        # Round all values to 18 decimal places.
        content[CHEI] = str(round(float(content[CHEI]), 18))
        content[BHEI] = str(round(float(content[BHEI]), 18))
        content[BWEI] = str(round(float(content[BWEI]), 18))
        return content


def read_userline(user_id, line):
    content = read_user(user_id)
    return content[line - 1]


# Write to specific user.
def write_user(user_id, content):
    user_id = str(user_id)
    # Replace None.
    if content[BWEI] == "None" + newline:
        content[BWEI] = str(defaultweight) + newline
    if content[BHEI] == "None" + newline:
        content[BHEI] = str(defaultweight) + newline
    if content[CHEI] == "None" + newline:
        content[CHEI] = content[3]
    # Round all values to 18 decimal places.
    content[CHEI] = str(round(float(content[CHEI]), 18))
    content[BHEI] = str(round(float(content[BHEI]), 18))
    content[BWEI] = str(round(float(content[BWEI]), 18))
    # Add new line characters to entries that don't have them.
    for idx, item in enumerate(content):
        if not content[idx].endswith("\n"):
            content[idx] = content[idx] + "\n"
    # Delete userfile.
    os.remove(folder + "/users/" + user_id + ".txt")
    # Make a new userfile.
    with open(folder + "/users/" + user_id + ".txt", "w+") as userfile:
        # Write content to lines.
        userfile.writelines(content)


def isFeetAndInchesAndIfSoFixIt(input):
    regex = r"^(?P<feet>\d+(ft|foot|feet|\'))(?P<inch>\d+(in|\")*)"
    m = re.match(regex, input, flags=re.I)
    if not m:
        return input
    wholefeet = m.group('feet')
    wholeinch = m.group('inch')
    feet = getnum(wholefeet)
    inch = getnum(wholeinch)
    if feet is None:
        feet = 0
    if inch is None:
        inch = 0
    totalinches = (feet * 12) + inch
    return f"{totalinches}in"


# Count users.
members = 0
path = folder + '/users'
listing = os.listdir(path)
for infile in listing:
    if infile.endswith(".txt"):
        members += 1
logger.load("Loaded {0} users.".format(members))

enspace = "\u2002"
printtab = enspace * 4


# Slow growth tasks.
tasks = {}

# Unit constants.
# Height [micrometers]
inch = Decimal("25400")
foot = inch * Decimal("12")
mile = foot * Decimal("5280")
ly = mile * Decimal("5879000000000")
au = Decimal("149597870700000000")
uni = Decimal("879848000000000000000000000000000")
infinity = Decimal("879848000000000000000000000000000000000000000000000000000000")
# Weight [milligrams]
ounce = Decimal("28350")
pound = ounce * Decimal("16")
uston = pound * Decimal("2000")
earth = Decimal("5972198600000000000000000000000")
sun = Decimal("1988435000000000000000000000000000000")
milkyway = Decimal("95000000000000000000000000000000000000000000000")
uniw = Decimal("3400000000000000000000000000000000000000000000000000000000000")


# Convert any supported height to 'size value'
def toSV(value, unit):
    if value is None or unit is None:
        return None
    value = Decimal(value)
    unitlower = unit.lower()
    if unitlower in ["yoctometers", "yoctometer"] or unit == "ym":
        outputSV = value / Decimal("1E18")
    elif unitlower in ["zeptometers", "zeptometer"] or unit == "zm":
        outputSV = value / Decimal("1E15")
    elif unitlower in ["attometers", "attometer"] or unit == "am":
        outputSV = value / Decimal("1E12")
    elif unitlower in ["femtometers", "femtometer"] or unit == "fm":
        outputSV = value / Decimal("1E9")
    elif unitlower in ["picometers", "picometer"] or unit == "pm":
        outputSV = value / Decimal("1E6")
    elif unitlower in ["nanometers", "nanometer"] or unit == "nm":
        outputSV = value / Decimal("1E3")
    elif unitlower in ["micrometers", "micrometer"] or unit in ["um", "µm"]:
        outputSV = value
    elif unitlower in ["millimeters", "millimeter"] or unit == "mm":
        outputSV = value * Decimal("1E3")
    elif unitlower in ["centimeters", "centimeter"] or unit == "cm":
        outputSV = value * Decimal("1E4")
    elif unitlower in ["meters", "meter"] or unit == "m":
        outputSV = value * Decimal("1E6")
    elif unitlower in ["kilometers", "kilometer"] or unit == "km":
        outputSV = value * Decimal("1E9")
    elif unitlower in ["megameters", "megameter"] or unit == "Mm":
        outputSV = value * Decimal("1E12")
    elif unitlower in ["gigameters", "gigameter"] or unit == "Gm":
        outputSV = value * Decimal("1E15")
    elif unitlower in ["terameters", "terameter"] or unit == "Tm":
        outputSV = value * Decimal("1E18")
    elif unitlower in ["petameters", "petameter"] or unit == "Pm":
        outputSV = value * Decimal("1E21")
    elif unitlower in ["exameters", "exameter"] or unit == "Em":
        outputSV = value * Decimal("1E24")
    elif unitlower in ["zettameters", "zettameter"] or unit == "Zm":
        outputSV = value * Decimal("1E27")
    elif unitlower in ["yottameters", "yottameter"] or unit == "Ym":
        outputSV = value * Decimal("1E30")
    elif unitlower in ["inches", "inch", "in", "\""]:
        outputSV = value * inch
    elif unitlower in ["feet", "foot", "ft", "\'"]:
        outputSV = value * foot
    elif unitlower in ["miles", "mile", "mi"]:
        outputSV = value * mile
    elif unitlower in ["lightyears", "lightyear"] or unit == "ly":
        outputSV = value * ly
    elif unitlower in ["astronomical_units", "astronomical_unit"] or unit == "AU":
        outputSV = value * au
    elif unitlower in ["universes", "universe"] or unit == "uni":
        outputSV = value * uni
    elif unitlower in ["kilouniverses", "kilouniverse"] or unit == "kuni":
        outputSV = value * uni * Decimal("1E3")
    elif unitlower in ["megauniverses", "megauniverse"] or unit == "Muni":
        outputSV = value * uni * Decimal("1E6")
    elif unitlower in ["gigauniverses", "gigauniverse"] or unit == "Guni":
        outputSV = value * uni * Decimal("1E9")
    elif unitlower in ["terauniverses", "terauniverse"] or unit == "Tuni":
        outputSV = value * uni * Decimal("1E12")
    elif unitlower in ["petauniverses", "petauniverse"] or unit == "Puni":
        outputSV = value * uni * Decimal("1E15")
    elif unitlower in ["exauniverses", "exauniverse"] or unit == "Euni":
        outputSV = value * uni * Decimal("1E18")
    elif unitlower in ["zettauniverses", "zettauniverse"] or unit == "Zuni":
        outputSV = value * uni * Decimal("1E21")
    elif unitlower in ["yottauniverses", "yottauniverse"] or unit == "Yuni":
        outputSV = value * uni * Decimal("1E24")
    else:
        return None
    return outputSV


# Convert 'size values' to a more readable format (metric to 3 decimal places)
def fromSVacc(value):
    return fromSV(value, 3)


# Convert 'size values' to a more readable format (metric)
def fromSV(value, accuracy=2):
    value = Decimal(value)
    output = ""
    if value <= Decimal("0"):
        return "0"

    if value < Decimal("1E-15"):
        scale, unit = Decimal("1E-18"), "ym"
    elif value < Decimal("1E-12"):
        scale, unit = Decimal("1E-15"), "zm"
    elif value < Decimal("1E-9"):
        scale, unit = Decimal("1E-12"), "am"
    elif value < Decimal("1E-6"):
        scale, unit = Decimal("1E-9"), "fm"
    elif value < Decimal("1E-3"):
        scale, unit = Decimal("1E-6"), "pm"
    elif value < Decimal("1E0"):
        scale, unit = Decimal("1E-3"), "nm"
    elif value < Decimal("1E2"):
        scale, unit = Decimal("1E0"), "µm"
    elif value < Decimal("1E4"):
        scale, unit = Decimal("1E3"), "mm"
    elif value < Decimal("1E6"):
        scale, unit = Decimal("1E4"), "cm"
    elif value < Decimal("1E9"):
        scale, unit = Decimal("1E6"), "m"
    elif value < Decimal("1E12"):
        scale, unit = Decimal("1E9"), "km"
    elif value < Decimal("1E15"):
        scale, unit = Decimal("1E12"), "Mm"
    elif value < Decimal("1E18"):
        scale, unit = Decimal("1E15"), "Gm"
    elif value < Decimal("1E21"):
        scale, unit = Decimal("1E18"), "Tm"
    elif value < Decimal("1E24"):
        scale, unit = Decimal("1E21"), "Pm"
    elif value < Decimal("1E27"):
        scale, unit = Decimal("1E24"), "Em"
    elif value < Decimal("1E30"):
        scale, unit = Decimal("1E27"), "Zm"
    elif value < uni:
        scale, unit = Decimal("1E30"), "Ym"
    elif value < uni * Decimal("1E3"):
        scale, unit = uni, "uni"
    elif value < uni * Decimal("1E6"):
        scale, unit = uni * Decimal("1E3"), "kuni"
    elif value < uni * Decimal("1E9"):
        scale, unit = uni * Decimal("1E6"), "Muni"
    elif value < uni * Decimal("1E12"):
        scale, unit = uni * Decimal("1E9"), "Guni"
    elif value < uni * Decimal("1E15"):
        scale, unit = uni * Decimal("1E12"), "Tuni"
    elif value < uni * Decimal("1E18"):
        scale, unit = uni * Decimal("1E15"), "Puni"
    elif value < uni * Decimal("1E21"):
        scale, unit = uni * Decimal("1E18"), "Euni"
    elif value < uni * Decimal("1E24"):
        scale, unit = uni * Decimal("1E21"), "Zuni"
    elif value < uni * Decimal("1E27"):
        scale, unit = uni * Decimal("1E24"), "Yuni"
    else:
        return "∞"
    return output

    return f"{round(trimzeroes(value) * scale, accuracy)}{unit}"


# Convert 'size values' to a more readable format (USA)
def fromSVUSA(value, accuracy=2):
    value = Decimal(value)
    output = ""
    if value <= Decimal("0"):
        return "0"

    if value < Decimal("1E-15"):
        scale, unit = Decimal("1E-18"), "ym"
    elif value < Decimal("1E-12"):
        scale, unit = Decimal("1E-15"), "zm"
    elif value < Decimal("1E-9"):
        scale, unit = Decimal("1E-12"), "am"
    elif value < Decimal("1E-6"):
        scale, unit = Decimal("1E-9"), "fm"
    elif value < Decimal("1E-3"):
        scale, unit = Decimal("1E-6"), "pm"
    elif value < Decimal("1E0"):
        scale, unit = Decimal("1E-3"), "nm"
    elif value < Decimal("1E2"):
        scale, unit = Decimal("1E0"), "µm"
    elif value < Decimal("1E4"):
        scale, unit = Decimal("1E3"), "mm"
    elif value < foot:
        scale, unit = inch, "in"
    elif value < mile:
        inchval = value / inch                  # convert to inches
        feetval, inchval = divmod(inchval, 12)  # divide by 12 to get feet, and the remainder inches
        roundedinchval = round(inchval, accuracy)
        return f"{feetval}'{inchval}\""
    elif value < au:
        scale, unit = mile, "mi"
    elif value < ly:
        scale, unit = au, "AU"
    elif value < uni / 10:
        scale, unit = ly, "ly"
    elif value < uni * Decimal("1E3"):
        scale, unit = uni, "uni"
    elif value < uni * Decimal("1E6"):
        scale, unit = uni * Decimal("1E3"), "kuni"
    elif value < uni * Decimal("1E9"):
        scale, unit = uni * Decimal("1E6"), "Muni"
    elif value < uni * Decimal("1E12"):
        scale, unit = uni * Decimal("1E9"), "Guni"
    elif value < uni * Decimal("1E15"):
        scale, unit = uni * Decimal("1E12"), "Tuni"
    elif value < uni * Decimal("1E18"):
        scale, unit = uni * Decimal("1E15"), "Puni"
    elif value < uni * Decimal("1E21"):
        scale, unit = uni * Decimal("1E18"), "Euni"
    elif value < uni * Decimal("1E24"):
        scale, unit = uni * Decimal("1E21"), "Zuni"
    elif value < uni * Decimal("1E27"):
        scale, unit = uni * Decimal("1E24"), "Yuni"
    else:
        return "∞"

    return f"{round(trimzeroes(value) * scale, accuracy)}{unit}"


# Convert any supported weight to 'weight value', or milligrams.
def toWV(value, unit):
    value = Decimal(value)
    unitlower = unit.lower()
    if unitlower in ["yoctograms", "yoctograms"] or unit == "yg":
        output = value / Decimal("1E21")
    elif unitlower in ["zeptograms", "zeptograms"] or unit == "zg":
        output = value / Decimal("1E18")
    elif unitlower in ["attograms", "attogram"] or unit == "ag":
        output = value / Decimal("1E15")
    elif unitlower in ["femtogram", "femtogram"] or unit == "fg":
        output = value / Decimal("1E12")
    elif unitlower in ["picogram", "picogram"] or unit == "pg":
        output = value / Decimal("1E9")
    elif unitlower in ["nanogram", "nanogram"] or unit == "ng":
        output = value / Decimal("1E6")
    elif unitlower in ["microgram", "microgram"] or unit in ["ug", "µg"]:
        output = value / Decimal("1E3")
    elif unitlower in ["milligrams", "milligram"] or unit == "mg":
        output = value
    elif unitlower in ["grams", "gram"] or unit == "g":
        output = value * Decimal("1E3")
    elif unitlower in ["kilograms", "kilogram"] or unit == "kg":
        output = value * Decimal("1E6")
    elif unitlower in ["megagrams", "megagram", "ton", "tons", "tonnes", "tons"] or unit == "t":
        output = value * Decimal("1E9")
    elif unitlower in ["gigagrams", "gigagram", "kilotons", "kiloton", "kilotonnes", "kilotonne"] or unit in ["Gg", "kt"]:
        output = value * Decimal("1E12")
    elif unitlower in ["teragrams", "teragram", "megatons", "megaton", "megatonnes", "megatonne"] or unit in ["Tg", "Mt"]:
        output = value * Decimal("1E15")
    elif unitlower in ["petagrams", "petagram", "gigatons", "gigaton", "gigatonnes", "gigatonnes"] or unit in ["Pg", "Gt"]:
        output = value * Decimal("1E18")
    elif unitlower in ["exagrams", "exagram", "teratons", "teraton", "teratonnes", "teratonne"] or unit in ["Eg", "Tt"]:
        output = value * Decimal("1E21")
    elif unitlower in ["zettagrams", "zettagram", "petatons", "petaton", "petatonnes", "petatonne"] or unit in ["Zg", "Pt"]:
        output = value * Decimal("1E24")
    elif unitlower in ["yottagrams", "yottagram", "exatons", "exaton", "exatonnes", "exatonne"] or unit in ["Yg", "Et"]:
        output = value * Decimal("1E27")
    elif unitlower in ["zettatons", "zettaton", "zettatonnes", "zettatonne"] or unit == "Zt":
        output = value * Decimal("1E30")
    elif unitlower in ["yottatons", "yottaton", "yottatonnes", "yottatonne"] or unit == "Yt":
        output = value * Decimal("1E33")
    elif unitlower in ["universes", "universe"] or unit == "uni":
        output = value * uniw
    elif unitlower in ["kilouniverses", "kilouniverse"] or unit == "kuni":
        output = value * uniw * Decimal("1E3")
    elif unitlower in ["megauniverses", "megauniverse"] or unit == "Muni":
        output = value * uniw * Decimal("1E6")
    elif unitlower in ["gigauniverses", "gigauniverse"] or unit == "Guni":
        output = value * uniw * Decimal("1E9")
    elif unitlower in ["terauniverses", "terauniverse"] or unit == "Tuni":
        output = value * uniw * Decimal("1E12")
    elif unitlower in ["petauniverses", "petauniverse"] or unit == "Puni":
        output = value * uniw * Decimal("1E15")
    elif unitlower in ["exauniverses", "exauniverse"] or unit == "Euni":
        output = value * uniw * Decimal("1E18")
    elif unitlower in ["zettauniverses", "zettauniverse"] or unit == "Zuni":
        output = value * uniw * Decimal("1E21")
    elif unitlower in ["yottauniverses", "yottauniverse"] or unit == "Yuni":
        output = value * uniw * Decimal("1E24")
    elif unitlower in ["ounces", "ounce"] or unit == "oz":
        output = value * ounce
    elif unitlower in ["pounds", "pound"] or unit in ["lb", "lbs"]:
        output = value * pound
    elif unitlower in ["earth", "earths"]:
        output = value * earth
    elif unitlower in ["sun", "suns"]:
        output = value * sun
    else:
        return None
    return output


# Convert 'weight values' to a more readable format
def fromWV(value, accuracy=1):
    value = Decimal(value)
    if value <= Decimal("0"):
        return "0"
    if value < Decimal("1E-18"):
        scale, unit = Decimal("1E-21"), "yg"
    elif value < Decimal("1E-15"):
        scale, unit = Decimal("1E-18"), "zg"
    elif value < Decimal("1E-12"):
        scale, unit = Decimal("1E-15"), "ag"
    elif value < Decimal("1E-9"):
        scale, unit = Decimal("1E-12"), "fg"
    elif value < Decimal("1E-6"):
        scale, unit = Decimal("1E-9"), "pg"
    elif value < Decimal("1E-3"):
        scale, unit = Decimal("1E-6"), "ng"
    elif value < Decimal("1E0"):
        scale, unit = Decimal("1E-3"), "µg"
    elif value < Decimal("1E3"):
        scale, unit = Decimal("1E0"), "mg"
    elif value < Decimal("1E6"):
        scale, unit = Decimal("1E3"), "g"
    elif value < Decimal("1E9"):
        scale, unit = Decimal("1E6"), "kg"
    elif value < Decimal("1E12"):
        scale, unit = Decimal("1E9"), "t"
    elif value < Decimal("1E15"):
        scale, unit = Decimal("1E12"), "kt"
    elif value < Decimal("1E18"):
        scale, unit = Decimal("1E15"), "Mt"
    elif value < Decimal("1E21"):
        scale, unit = Decimal("1E18"), "Gt"
    elif value < Decimal("1E24"):
        scale, unit = Decimal("1E21"), "Tt"
    elif value < Decimal("1E27"):
        scale, unit = Decimal("1E24"), "Pt"
    elif value < Decimal("1E30"):
        scale, unit = Decimal("1E27"), "Et"
    elif value < Decimal("1E33"):
        scale, unit = Decimal("1E30"), "Zt"
    elif value < uniw:
        scale, unit = Decimal("1E33"), "Yt"
    elif value < uniw * Decimal("1E3"):
        scale, unit = uniw, "uni"
    elif value < uniw * Decimal("1E6"):
        scale, unit = uniw * Decimal("1E3"), "kuni"
    elif value < uniw * Decimal("1E9"):
        scale, unit = uniw * Decimal("1E6"), "Muni"
    elif value < uniw * Decimal("1E12"):
        scale, unit = uniw * Decimal("1E9"), "Guni"
    elif value < uniw * Decimal("1E15"):
        scale, unit = uniw * Decimal("1E12"), "Tuni"
    elif value < uniw * Decimal("1E18"):
        scale, unit = uniw * Decimal("1E15"), "Puni"
    elif value < uniw * Decimal("1E21"):
        scale, unit = uniw * Decimal("1E18"), "Euni"
    elif value < uniw * Decimal("1E24"):
        scale, unit = uniw * Decimal("1E21"), "Zuni"
    elif value < uniw * Decimal("1E27"):
        scale, unit = uniw * Decimal("1E24"), "Yuni"
    else:
        return "∞"

    return f"{round(trimzeroes(value) * scale, accuracy)}{unit}"


# Convert 'weight values' to a more readable format (USA)
def fromWVUSA(value, accuracy=1):
    value = Decimal(value)
    if value == 0:
        return "almost nothing"
    if value < Decimal("1E-18"):
        scale, unit = Decimal("1E-21"), "yg"
    elif value < Decimal("1E-15"):
        scale, unit = Decimal("1E-18"), "zg"
    elif value < Decimal("1E-12"):
        scale, unit = Decimal("1E-15"), "ag"
    elif value < Decimal("1E-9"):
        scale, unit = Decimal("1E-12"), "fg"
    elif value < Decimal("1E-6"):
        scale, unit = Decimal("1E-9"), "pg"
    elif value < Decimal("1E-3"):
        scale, unit = Decimal("1E-6"), "ng"
    elif value < Decimal("1E0"):
        scale, unit = Decimal("1E-3"), "µg"
    elif value < Decimal("1E3"):
        scale, unit = Decimal("1E0"), "mg"
    elif value < ounce / 10:
        scale, unit = Decimal("1E3"), "g"
    elif value < pound:
        scale, unit = ounce, "oz"
    elif value < uston:
        scale, unit = pound, "lb"
    elif value < earth / 10:
        scale, unit = uston, " US tons"
    elif value < sun / 10:
        scale, unit = earth, "Earths"
    elif value < milkyway:
        scale, unit = sun, " Suns"
    elif value < uniw:
        scale, unit = milkyway, " Milky Ways"
    elif value < uniw * Decimal("1E3"):
        scale, unit = uniw, "uni"
    elif value < uniw * Decimal("1E6"):
        scale, unit = uniw / Decimal("1E3"), "kuni"
    elif value < uniw * Decimal("1E9"):
        scale, unit = uniw / Decimal("1E6"), "Muni"
    elif value < uniw * Decimal("1E12"):
        scale, unit = uniw / Decimal("1E9"), "Guni"
    elif value < uniw * Decimal("1E15"):
        scale, unit = uniw / Decimal("1E12"), "Tuni"
    elif value < uniw * Decimal("1E18"):
        scale, unit = uniw / Decimal("1E15"), "Puni"
    elif value < uniw * Decimal("1E21"):
        scale, unit = uniw / Decimal("1E18"), "Euni"
    elif value < uniw * Decimal("1E24"):
        scale, unit = uniw / Decimal("1E21"), "Zuni"
    elif value < uniw * Decimal("1E27"):
        scale, unit = uniw / Decimal("1E24"), "Yuni"
    else:
        return "∞"

    return f"{round(trimzeroes(value) * scale, accuracy)}{unit}"


def toShoeSize(footlength):
    child = False
    footlengthinches = Decimal(footlength / inch)
    shoesize = 3 * footlengthinches
    shoesize = shoesize - 22
    if shoesize < 1:
        child = True
        shoesize += 12 + Decimal(1 / 3)
    if shoesize < 1:
        return "No shoes exist this small!"
    shoesize = place_value(round_nearest_half(shoesize))
    if child:
        shoesize = "Children's " + shoesize
    return "Size US " + shoesize

# Currently unused.


def fromShoeSize(size):
    child = False
    if "c" in size.toLower():
        child = True
    size = getnum(size)
    inches = Decimal(size) + 22
    if child:
        inches = Decimal(size) + 22 - 12 - (1 / 3)
    inches = inches / Decimal(3)
    out = inches * inch
    return out


def check(ctx):
    # Disable commands for users with the SizeBot_Banned role.
    if not isinstance(ctx.channel, discord.abc.GuildChannel):
        return False

    role = discord.utils.get(ctx.author.roles, name='SizeBot_Banned')
    return role is None


logger.load("Global functions loaded.")
