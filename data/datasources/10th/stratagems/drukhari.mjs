import { TURN, TYPE, PHASE } from './CONSTANTS.mjs';

const detachment = { 'Realspace Raiders': 'Realspace Raiders', 'Skysplinter Assault': 'Skysplinter Assault' };

const template = [
  {
    name: 'PREY ON THE WEAK',
    cost: 1,
    type: TYPE['Battle Tactic'],
    detachment: detachment['Realspace Raiders'],
    turn: TURN.your,
    phase: [PHASE.shooting],
    fluff: `The scent of a foe in pain draws Drukhari to it like hungry predators to an injured beast, their senses sharpening at its tang.`,
    when: ` Your Shooting phase.`,
    target: `One KABAL unit from your army and one enemy unit that is Below Half-strength.`,
    effect: `Until the end of the phase, each time a model in your unit makes an attack that targets that enemy unit, you can re-roll the Wound roll.`,
    restrictions: ``,
  },
  {
    name: 'STRIKE AND FADE',
    cost: 2,
    type: TYPE['Epic Deed'],
    detachment: detachment['Realspace Raiders'],
    turn: TURN.your,
    phase: [PHASE.shooting],
    fluff: `The Drukhari are masters at using hit-and-run tactics, engaging a target with a flurry of shots before quickly manoeuvring into cover or out of sight.`,
    when: `End of your Shooting phase.`,
    target: `One DRUKHARI unit from your army (excluding AIRCRAFT).
    `,
    effect: `Your unit can immediately make a Normal move.`,
    restrictions: `Until the end of the turn, your unit is not eligible to declare a charge and that unit cannot embark within a TRANSPORT at the end of this move.`,
  },
  {
    name: 'ACROBATIC DISPLAY',
    cost: 1,
    type: TYPE['Epic Deed'],
    detachment: detachment['Realspace Raiders'],
    turn: TURN.your,
    phase: [PHASE.charge],
    fluff: `Many Wych Cults favour spectacular gymnastic displays. Their fighters are never still, springing from one foot to the other at blinding speed.`,
    when: `Your Charge phase.`,
    target: `One WYCH CULT unit from your army.`,
    effect: `Until the end of the phase, your unit is eligible to declare a charge even if it Fell Back or Advanced this turn.`,
    restrictions: ``,
  },
  {
    name: 'ALLIANCE OF AGONY',
    cost: 1,
    type: TYPE['Battle Tactic'],
    detachment: detachment['Realspace Raiders'],
    turn: TURN.either,
    phase: [PHASE.any],
    fluff: `Even the most bloodthirsty Drukhari will veil their enmity to work together against a shared enemy for the same gruesome purpose.`,
    when: `Start of any phase.`,
    target: `One ARCHON, one SUCCUBUS and one HAEMONCULUS from your army.`,
    effect: `Discard one Pain token from your Pain token pool. Until the end of the phase, all three of those models’ units are Empowered.`,
    restrictions: `You can only use this Stratagem if you are able to select all three of the target models stated above.`,
  },
  {
    name: 'QUICKSILVER REACTIONS',
    cost: 1,
    type: TYPE['Battle Tactic'],
    detachment: detachment['Realspace Raiders'],
    turn: TURN.either,
    phase: [PHASE.shooting, PHASE.fight],
    fluff: `The hyper-fast reflexes of the Drukhari allow them to duck and weave to avoid all but the swiftest enemy strikes.`,
    when: `Your opponent’s Shooting phase or the Fight phase, just after an enemy unit has selected its targets.`,
    target: `One DRUKHARI unit from your army that was selected as the target of one or more of the attacking unit’s attacks.`,
    effect: `Until the end of the phase, each time an attack that targets your unit, subtract 1 from the Hit roll.`,
    restrictions: `You cannot target a HAEMONCULUS COVENS unit from your army for this Stratagem.`,
  },
  {
    name: 'INSENSIBLE TO PAIN',
    cost: 1,
    type: TYPE['Battle Tactic'],
    detachment: detachment['Realspace Raiders'],
    turn: TURN.either,
    phase: [PHASE.shooting, PHASE.fight],
    fluff: `The twisted creations of the Haemonculus Covens are insensible to all but the most mortal injuries.`,
    when: `Your opponent’s Shooting phase or the Fight phase, just after an enemy unit has selected its targets.`,
    target: `One HAEMONCULUS COVENS unit from your army that was selected as the target of one or more of the attacking unit’s attacks.`,
    effect: `Until the end of the phase, each time an attack targets your unit, subtract 1 from the Wound roll.`,
    restrictions: ``,
  },
  {
    name: 'VICIOUS BLADES',
    cost: 1,
    type: TYPE['Strategic Ploy'],
    detachment: detachment['Skysplinter Assault'],
    turn: TURN.either,
    phase: [PHASE.fight],
    fluff: `Wielding a horrifying array of hooked boarding blades, barbed lariats and other specialised tools of agony, these warriors hack and slash at their foes even as their transport skims low overhead.`,
    when: `Fight phase, just after a DRUKHARI TRANSPORT from your army has selected its targets.`,
    target: `That TRANSPORT.`,
    effect: `After your TRANSPORT has fought, select one enemy unit that was the target of one or more of those attacks and roll one D6 for each model embarked within your TRANSPORT, adding 1 to the result if that embarked model is a WRACKS model: for each 5+, that enemy unit suffers 1 mortal wound (to a maximum of 6 mortal wounds).`,
    restrictions: ``,
  },
  {
    name: 'WRAITHLIKE RETREAT',
    cost: 1,
    type: TYPE['Strategic Ploy'],
    detachment: detachment['Skysplinter Assault'],
    turn: TURN.either,
    phase: [PHASE.fight],
    fluff: `Employing smoke grenades, paralysing mists or simple cunning and agility, these warriors slip away like spectres.`,
    when: `End of the Fight phase.`,
    target: `One DRUKHARI INFANTRY unit from your army that fought this phase.`,
    effect: `Your unit can make a Normal or Fall Back move, but unless it is a WYCHES unit, it must end that move wholly within 3" horizontally and 5" vertically of a friendly DRUKHARI TRANSPORT and must embark within that TRANSPORT at the end of that move.`,
    restrictions: ``,
  },
  {
    name: 'POUNCE ON THE PREY',
    cost: 1,
    type: TYPE['Strategic Ploy'],
    detachment: detachment['Skysplinter Assault'],
    turn: TURN.your,
    phase: [PHASE.movement],
    fluff: `Incredible alien agility and a delight in taking wild risks help these warriors to leap acrobatically from their skimming transports directly into battle.`,
    when: `Your Movement phase, just after a DRUKHARI INFANTRY unit from your army disembarks from a TRANSPORT that made a Normal move this phase.`,
    target: `That INFANTRY unit.`,
    effect: `Until the end of the turn, your unit is eligible to declare a charge.`,
    restrictions: ``,
  },
  {
    name: 'SKYBORNE ANNIHILATION',
    cost: 1,
    type: TYPE['Battle Tactic'],
    detachment: detachment['Skysplinter Assault'],
    turn: TURN.your,
    phase: [PHASE.shooting],
    fluff: `These warriors are well versed in raining suppressing fire on the foe even as they close with them from on high, shredding defences and leaving the survivors easy prey for the raid.`,
    when: `Your Shooting phase.`,
    target: `One DRUKHARI unit from your army that disembarked from a TRANSPORT this turn and has not been selected to shoot this phase.`,
    effect: `Until the end of the phase, ranged weapons equipped by models in your unit have the [SUSTAINED HITS 1] ability, or the [SUSTAINED HITS 2] ability instead if it is a KABALITE WARRIORS unit.`,
    restrictions: ``,
  },
  {
    name: 'SWOOPING MOCKERY',
    cost: 1,
    type: TYPE['Battle Tactic'],
    detachment: detachment['Skysplinter Assault'],
    turn: TURN.your,
    phase: [PHASE.movement],
    fluff: `The crew of this skimmer delight in evading and taunting their enemies with mocking ease.`,
    when: `Your opponent’s Movement phase, just after an enemy unit ends a Normal, Advance or Fall Back move.`,
    target: `One DRUKHARI TRANSPORT from your army that is not within Engagement Range of one or more enemy units and is within 9" of the enemy unit that just ended that move.`,
    effect: `Your TRANSPORT can make a Normal move of up to 6".`,
    restrictions: ``,
  },
  {
    name: 'NIGHT SHIELD',
    cost: 1,
    type: TYPE['Battle Tactic'],
    detachment: detachment['Skysplinter Assault'],
    turn: TURN.your,
    phase: [PHASE.movement],
    fluff: `These powerful Drukhari devices occlude their raiding vehicles not only from physical sight but also targeting sensors and even psychic senses.`,
    when: `Your opponent’s Shooting phase, just after an enemy unit has selected its targets.`,
    target: `One DRUKHARI VEHICLE unit from your army that was selected as the target of one or more of the attacking unit’s attacks.`,
    effect: `Until the end of the phase, your unit has a 4+ invulnerable save.`,
    restrictions: ``,
  },
];

export default template;