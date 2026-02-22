ALTIS CROSSFIRE - Campaign Briefing Menu
=========================================

This folder is an Arma 3 MISSION PACKAGE. At mission start, a custom dialog opens with tabs so players can read the campaign lore, characters, factions, and mission arc in-game.

WHAT'S INCLUDED
----------------
  description.ext     - Defines the briefing dialog (tabs: Lore, Characters, Factions, Missions, Close)
  initPlayerLocal.sqf - Opens the dialog 1.5 seconds after the player loads (SP or MP)
  scripts/
    briefingMenu.sqf  - Fills each tab with text from the Altis Crossfire campaign; handles tab switching

HOW TO USE
----------
1. Copy the entire "AltisCrossfire_Briefing" folder into your Arma 3 missions directory:
   - Singleplayer: Documents\Arma 3\missions\
   - Multiplayer (server): use as your mission folder or merge with an existing mission

2. If you already have a mission with its own description.ext:
   - Merge the "class RscDisplayAltisCrossfireBriefing" block from this description.ext into yours.
   - Merge the onLoad and any needed controls if you use a different idd.

3. If you already have initPlayerLocal.sqf:
   - Add the createDialog call to your existing init (see initPlayerLocal.sqf contents).

4. Ensure scripts\briefingMenu.sqf is in the mission root under "scripts".

5. Launch the mission. The briefing menu opens automatically; use the tabs to read, then click Close.

REQUIREMENTS
------------
  - Arma 3 (vanilla; no CBA or other mods required)
  - Mission runs with 2ACW / Altis Crossfire context (the text references your campaign)

CUSTOMIZATION
-------------
  - Edit scripts\briefingMenu.sqf to change the text for Lore, Characters, Factions, or Missions.
  - Edit description.ext to change layout, colors, or button labels.
  - To open the menu again later (e.g. from an action): createDialog "RscDisplayAltisCrossfireBriefing";
