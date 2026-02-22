/*
 * Altis Crossfire - Open campaign briefing menu at mission start.
 * Screen starts black, menu shows, then fades in when player closes it.
 * Vanilla Arma 3, no mods required.
 */

if (!hasInterface) exitWith {};

[] spawn {
    waitUntil { !isNull player };

    cutText ["", "BLACK OUT", 0];
    sleep 0.5;

    call compile preprocessFileLineNumbers "scripts\briefingMenu.sqf";

    sleep 0.3;
    createDialog "RscDisplayAltisCrossfireBriefing";
    sleep 0.3;
    ["lore"] call ACW_fnc_briefingTab;

    waitUntil { isNull (findDisplay 7300) };

    cutText ["", "BLACK IN", 3];
};
