## SizeBot3½

* ~~Don't import * globalsb~~
* ~~Clean up all the imports really~~
* ~~Follow and document style conventions~~
* ~~Prevent that error we keep getting on readuser~~
* Setup develop branch
* Host Sizebot Unstable on VPS
    * Setup automatic deployment of develop branch commits
* ~~Migrate legacy User constants to new User object~~
* ~~Formatting~~
    * ~~Replace .format() with f-strings~~
    * ~~Fix allowbrackets~~
    * ~~Fix flake8 linting to check for more issues~~
* ~~Fix Unicode handling for nicknames (if this is even possible)~~
* ~~Make a custom emoji dictionary~~
* Commands
    * Make register commands easier to use and give better use output (simpler usage and better defaults)
    * Change the way &slowchange works (&slowchange \<rate\>)
    * Create convert command (&convert \<size\> \<new unit\>)
    * Custom base height/weight for raw compares
    * Create eval command (for devs only)
    * Help command
    * Implement SB3's &roll command.
* Make SizeBot respond to DMs in a helpful way.
    * Allow users to use DM-safe commands in DMs (about, help, bug, donate, convert, roll) [are there more?]
    * Otherwise, tell them they have to other commands in a server.
* Separate command logic into modules.
    * Register commands
    * Size change commands
    * Size comparison commands
* Setup testing.
    * Register commands
    * Size change command
    * Size comparison commands
    * Dice rolling
    * Size conversion
* Unit formatting.
    * Custom trigger points for units (millimeters triggers 1 degree of magnitude early, megameters triggers 1 degree late.)
    * Flag some units as only input units and not display units.
* Basic English syntax for some commands.
* Command metadata
    * Can it be used in DMs?
    * Help strings
    * Remove brackets?
    * etc...
* Make DigiLogger an dDigiFormatter be imported from their seperate things instead of copy+pasting them in to the folder.
* Future proofing.
    * Make module functions that make command code easy to read, work with, and make new commands. [Digi calls this "the SizeAPI"]

#### Figure out database schema.

## SizeBot4

* Migrate to MariaDB
    * Make repeating tasks check the database every X time instead of asyncio tasks that are unwieldy
    * Guilds
    * Members
    * "Characters"
    * Winks
* Switchable user profiles (create characters, switch between them)
* Switch some things to embeds
* Replace digiSV with dunit
* Add support for multiple guilds
* Allow users to store character pictures
* Autostop option for slowchange
* Custom emojis trigger events
* Generate user "cards"
* Compare yourself to objects of similar size
* Auto-role based on current size option (optional for user)
* Allow users to change other users (on, blacklist, whitelist, off)
* NSFW stats<sup>?</sup>
* More customizables

### New Commands

* &slowspurt (&slowspurt \<rate\> \<interval\>)
* &statsnsfw \<user\>
* &statssuchthat [attribute] [size]
    * OR [attribute] [otheruser/othersize] [otherattribute]
    * OR [attribute] [otheruser/othersize] [otherattribute] [size]
* &statsnsfwsuchthat [attribute] [size]
    * OR [attribute] [otheruser/othersize] [otherattribute]
    * OR [attribute] [otheruser/othersize] [otherattribute] [size]
* &comparensfw [user1/size1] \<user2/size2\>
* &objectcompare \<user/size\> (&objcompare?)
* &setother \<user\> \<attribute\> \<value\>
* &changeother \<user\> \<attribute\> \<style\> \<amount\>
* &whitelist/blacklist [on/off, add/remove] \<users...\>
* &autorole [on/off]
* &schedule [date/time] [command...]
* &sudo [user] [command...]