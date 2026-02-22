/*
 * Altis Crossfire - Briefing Menu Content & Tab Logic
 * Run from initPlayerLocal.sqf BEFORE opening the dialog.
 * Defines global content strings and the tab-switching function.
 */

// ---- Content strings ----

ACW_content_lore = ""
+ "<t size='1.2' color='#d4a84b'>LORE / STORYLINE</t><br/><br/>"
+ "<t size='1.05' color='#a0b0d0'>How the War Started</t><br/>"
+ "The Second American Civil War (2ACW) didn't begin on a single day. It was years of political fracture: disputed elections, state secessions, and the collapse of trust between the federal government and large parts of the country. When President Dennison declared a 'national restoration' and ordered the military to 'pacify' regions that had voted for independence, units split. Some stayed loyal (Federalists). Others sided with breakaway states or the 'legitimate' government-in-exile (the NPA and its allies). Alaska, California, Hawaii, and others refused to obey federal orders. Texas declared neutrality and sold to everyone. Militias formed on both sides. The EU intervened with a 'humanitarian and stability' mission. The war went from standoffs to open fighting. No one has won. No one has surrendered.<br/><br/>"
+ "<t size='1.05' color='#a0b0d0'>Why It Spread Overseas</t><br/>"
+ "America's collapse didn't stay contained. The EU wanted to protect its interests. Breakaway states needed supply lines and legitimacy. The Federal government needed deniable ways to hit its enemies abroad. Texas, Florida Alliance, and mercenaries saw profit. So 'advisors,' 'contractors,' and 'humanitarian' missions appeared wherever the war could be fought by other means. The Mediterranean became one of those arenas. Altis was one of them.<br/><br/>"
+ "<t size='1.05' color='#a0b0d0'>Why Altis</t><br/>"
+ "Altis is an island in the Mediterranean. It has no standing army of its own. It's a strategic piece of real estate: a logistics hub, a place to train and run operations. When the 2ACW went global, every side wanted a piece. The EU set up a 'stability' presence. California and breakaway states established aid posts. Federalists sent 'training' detachments that were really combat units. National Guard, Police, Mercenaries, and independents moved in. Within months, Altis was no longer neutral. It was a second front.<br/><br/>"
+ "<t size='1.05' color='#a0b0d0'>The Situation Now</t><br/>"
+ "The island is divided into zones of influence. Federalists and National Guard hold key airfields and checkpoints. California runs a critical aid post near Kavala; the EU has a training base. Hawaii and Alaska have small footprints. NPA coordinates with the 'coalition.' Mercenaries and Pro-Dennison Militia carry out raids. Independents control villages and smuggling routes.<br/><br/>"
+ "Colonel Richard 'Dick' Harlow, the Federalist commander on Altis, is building something big in the north - a staging base for men and materiel. The coalition doesn't yet know the full picture.<br/><br/>"
+ "You're a contractor who got cut off when the fighting spread. You're not here to save the world. You're here to survive, protect your people, and maybe help decide who wins this corner of the war.<br/>";

ACW_content_characters = ""
+ "<t size='1.2' color='#d4a84b'>CHARACTERS</t><br/><br/>"
+ "<t size='1.0' color='#8090b0'>Player (you)</t><br/>"
+ "Your choice of name (suggested: Marcus Webb). Former US Army, separated before the 2ACW. You came to Altis as a contractor, got cut off, and now work for whoever keeps you and your team alive. No grand loyalty - you care about your people and the civilians caught in the crossfire.<br/><br/>"
+ "<t size='1.05' color='#a0b0d0'>--- ALLIES ---</t><br/><br/>"
+ "<t color='#c0d0f0'>Captain Elena Vasquez</t> <t color='#7888a0'>(California)</t><br/>"
+ "Runs the aid post near Kavala. Medic, de facto leader. Mission giver for convoys and rescues. Wants justice - then revenge - after Mercenaries hit her convoy.<br/><br/>"
+ "<t color='#c0d0f0'>Sgt. Dmitri 'Dima' Volkov</t> <t color='#7888a0'>(European Union)</t><br/>"
+ "Intel and joint ops. Ex-Eastern Bloc. Discovers Federalists are building a major staging base; torn between EU rules and what he knows must be done.<br/><br/>"
+ "<t color='#c0d0f0'>Lt. James 'Jimmy' Okuda</t> <t color='#7888a0'>(Hawaii)</t><br/>"
+ "Recon, drones, radio. Tracks a Federalist commander who turns out to be his former CO; moral choice between duty and past loyalty.<br/><br/>"
+ "<t color='#c0d0f0'>Cpl. Rosa Mendez</t> <t color='#7888a0'>(NPA)</t><br/>"
+ "Liaison to the coalition. By-the-book but pragmatic. Must decide whether to report Vasquez's revenge op or look the other way.<br/><br/>"
+ "<t color='#c0d0f0'>Maj. Tom Bradley</t> <t color='#7888a0'>(Alaska)</t><br/>"
+ "Logistics, supply routes. Cuts a deal with Texas for fuel; you can support or expose it.<br/><br/>"
+ "<t size='1.05' color='#a0b0d0'>--- ANTAGONISTS ---</t><br/><br/>"
+ "<t color='#d09090'>Col. Richard 'Dick' Harlow</t> <t color='#906060'>(Federalists)</t><br/>"
+ "Federalist commander on Altis. Ex-Special Forces. Building a staging base for a push back home. Orders a hit on Vasquez's clinic. Recurring villain until the finale.<br/><br/>"
+ "<t color='#d09090'>'Judge' Morrison</t> <t color='#906060'>(Pro-Dennison Militia)</t><br/>"
+ "Fanatical leader; 'people's courts' and reprisals. Optional mission to capture or eliminate him.<br/><br/>"
+ "<t color='#d09090'>Mercenary Commander</t> <t color='#906060'>(Mercenaries)</t><br/>"
+ "Voice on the radio; executes Federalist contracts. Ambushes, convoy hits. You raid his FOB in a night op.<br/><br/>"
+ "<t size='1.05' color='#a0b0d0'>--- INDEPENDENTS ---</t><br/><br/>"
+ "<t color='#b0c0a0'>'Doc' Rivera</t> <t color='#708060'>(Puerto Rico)</t><br/>"
+ "Medical station on the south coast. Healing, intel, safe house. Asks you to escort a Federalist defector; choice who gets him.<br/><br/>"
+ "<t color='#b0c0a0'>Carson Reed</t> <t color='#708060'>(Texas)</t><br/>"
+ "Arms dealer. Black-market missions; you can work with him or turn his deals over to allies.<br/><br/>"
+ "<t color='#b0c0a0'>Maria 'Mama' Kostas</t> <t color='#708060'>(Sheriff)</t><br/>"
+ "Holds a district together. Her son is conscripted by Pro-Dennison; rescue him for permanent Sheriff support.<br/><br/>"
+ "<t color='#b0c0a0'>Viktor</t> <t color='#708060'>(7CHAT)</t><br/>"
+ "Community leader; suspicious of outsiders. Bring supplies for intel; eventually reveals a hidden Federalist cache.<br/><br/>"
+ "<t color='#b0c0a0'>'Red'</t> <t color='#708060'>(Portland-Maoists)</t><br/>"
+ "Sabotage and propaganda; optional ally for one-off strikes. Hitting the Federalist tower costs NPA/EU reputation.<br/><br/>"
+ "<t color='#b0c0a0'>Old Man Hayes</t> <t color='#708060'>(Minutemen)</t><br/>"
+ "Holds a valley. Save his granddaughter for Minutemen as recon asset.<br/><br/>"
+ "<t color='#b0c0a0'>'Ghost'</t> <t color='#708060'>(Florida Alliance)</t><br/>"
+ "Smuggler, fixer. Offers to smuggle Harlow off the island; you can take the deal, refuse, or set a trap.<br/>";

ACW_content_factions = ""
+ "<t size='1.2' color='#d4a84b'>FACTIONS ON ALTIS</t><br/><br/>"
+ "<t size='1.05' color='#6090d0'>BLUFOR-ALIGNED</t><br/><br/>"
+ "<t color='#c0d0f0'>European Union</t> - Peacekeeping, stability, EU interests and refugees.<br/><br/>"
+ "<t color='#c0d0f0'>Alaska</t> - Pro-Union; intel and supply lines; logistics hub.<br/><br/>"
+ "<t color='#c0d0f0'>California</t> - Humanitarian aid, anti-Federalist ops; field hospital and depot near Kavala.<br/><br/>"
+ "<t color='#c0d0f0'>Hawaii</t> - Naval/air support, recon; small footprint, high intel value.<br/><br/>"
+ "<t color='#c0d0f0'>NPA</t> - 'Loyalist' force; prove legitimacy, hunt Federalist cells.<br/><br/>"
+ "<t size='1.05' color='#d06060'>OPFOR</t><br/><br/>"
+ "<t color='#d09090'>Federalists</t> - Main antagonist bloc; 'restore order'; any means to crush rivals.<br/><br/>"
+ "<t color='#d09090'>National Guard</t> - Federalist-aligned; airfields and checkpoints.<br/><br/>"
+ "<t color='#d09090'>Police</t> - Checkpoints, interrogations, 'pacification.'<br/><br/>"
+ "<t color='#d09090'>Pro-Dennison Militia</t> - Loyal to the Federal president; irregulars, IEDs, reprisals.<br/><br/>"
+ "<t color='#d09090'>Mercenaries</t> - Deniable contractors; hit squads, convoy raids.<br/><br/>"
+ "<t size='1.05' color='#80a060'>INDEPENDENT</t><br/><br/>"
+ "<t color='#b0c0a0'>Texas</t> - Arms dealer, neutral broker; works with anyone who pays.<br/><br/>"
+ "<t color='#b0c0a0'>Florida Alliance</t> - Smuggling, private security; black-market missions.<br/><br/>"
+ "<t color='#b0c0a0'>Minutemen</t> - Local defence; villages and farms; earn trust or make enemies.<br/><br/>"
+ "<t color='#b0c0a0'>Militia</t> - Ungoverned; anti-Federalist or bandit; unpredictable.<br/><br/>"
+ "<t color='#b0c0a0'>Portland-Maoists</t> - Propaganda and sabotage; uneasy ally against Federalists.<br/><br/>"
+ "<t color='#b0c0a0'>7CHAT</t> - Communal; control a town or valley; need supplies and protection.<br/><br/>"
+ "<t color='#b0c0a0'>Sheriff</t> - Local law; hold a district together.<br/><br/>"
+ "<t color='#b0c0a0'>Puerto Rico</t> - Medical and logistics on the south coast; neutral unless attacked.<br/>";

ACW_content_missions = ""
+ "<t size='1.2' color='#d4a84b'>MISSION ARC (10 MISSIONS)</t><br/><br/>"
+ "<t size='1.1' color='#a0b0d0'>ACT 1 - SURVIVORS</t><br/><br/>"
+ "<t color='#d4a84b'>1. Leftovers</t><br/>"
+ "Cut off near Kavala. Federalists and Militia are clashing. Link up with California (Vasquez) and secure the aid post.<br/><br/>"
+ "<t color='#d4a84b'>2. First Contact</t><br/>"
+ "EU (Dima) recon of a Federalist checkpoint. Hawaiian support (Jimmy). First mention of 'Harlow' and Mercenary activity.<br/><br/>"
+ "<t color='#d4a84b'>3. The Doctor's Price</t><br/>"
+ "Defend Doc Rivera's station from Pro-Dennison. Escort convoy to 7CHAT. Viktor doesn't trust you yet.<br/><br/>"
+ "<t size='1.1' color='#a0b0d0'>ACT 2 - ALLIANCES</t><br/><br/>"
+ "<t color='#d4a84b'>4. Texas Tea</t><br/>"
+ "Bradley needs fuel. Texas (Reed) has it - for a 'favour.' Redirect a Federalist convoy. Moral choice: do the deal or report it.<br/><br/>"
+ "<t color='#d4a84b'>5. Mama's Boy</t><br/>"
+ "Sheriff (Maria Kostas) asks you to get her son back from Pro-Dennison. Infiltration or assault. 'Judge' Morrison appears.<br/><br/>"
+ "<t color='#d4a84b'>6. Red Lines</t><br/>"
+ "Red (Portland-Maoists) offers to hit a Federalist broadcast tower. Accept or refuse. NPA warns against 'extremists.'<br/><br/>"
+ "<t color='#d4a84b'>7. Jimmy's Ghost</t><br/>"
+ "Raid the Mercenary FOB at night. Intel points to Harlow and a major Federalist operation.<br/><br/>"
+ "<t size='1.1' color='#a0b0d0'>ACT 3 - CROSSFIRE</t><br/><br/>"
+ "<t color='#d4a84b'>8. Vasquez's Revenge</t><br/>"
+ "Hit the Federalist cell that ordered the clinic strike. Dima and Mendez are split. Harlow escapes but you take a key lieutenant.<br/><br/>"
+ "<t color='#d4a84b'>9. The Valley</t><br/>"
+ "Defend the valley with Minutemen and allies against Federalists and Mercenaries.<br/><br/>"
+ "<t color='#d4a84b'>10. Altis Crossfire (Finale)</t><br/>"
+ "Coalition assaults Harlow's FOB in the north. Confront Harlow: capture, kill, or (optional) Ghost smuggles him out. Your choices shape the ending.<br/>";

// ---- Tab switching function ----

ACW_fnc_briefingTab = {
    params ["_tab"];
    private _display = findDisplay 7300;
    if (isNull _display) exitWith {};

    private _group = _display displayCtrl 7303;
    private _ctrl = _group controlsGroupCtrl 7302;

    private _text = switch (_tab) do {
        case "lore": { ACW_content_lore };
        case "chars": { ACW_content_characters };
        case "missions_arc": { ACW_content_factions };
        case "missions": { ACW_content_missions };
        default { ACW_content_lore };
    };

    _ctrl ctrlSetStructuredText parseText _text;

    private _h = ctrlTextHeight _ctrl;
    _ctrl ctrlSetPositionH _h;
    _ctrl ctrlCommit 0;

    {
        (_display displayCtrl _x) ctrlSetBackgroundColor [0.2, 0.25, 0.35, 0.9];
    } forEach [7310, 7311, 7312, 7314];

    private _activeIdc = switch (_tab) do {
        case "lore": { 7310 };
        case "chars": { 7311 };
        case "missions_arc": { 7312 };
        case "missions": { 7314 };
        default { 7310 };
    };
    (_display displayCtrl _activeIdc) ctrlSetBackgroundColor [0.35, 0.4, 0.55, 1];
};

// ---- Close menu and fade screen in ----
ACW_fnc_briefingClose = {
    closeDialog 0;
    createDialog "RscDisplayAltisCrossfireFade";

    waitUntil { !isNull findDisplay 7301 };
    private _ctrl = (findDisplay 7301) displayCtrl 7302;
    if (isNull _ctrl) exitWith { closeDialog 0; };

    private _duration = 1.5;
    private _steps = 30;
    private _step = 1 / _steps;
    private _sleep = _duration / _steps;

    for "_i" from 0 to 1 step _step do {
        _ctrl ctrlSetFade _i;
        sleep _sleep;
    };

    closeDialog 7301;
};
