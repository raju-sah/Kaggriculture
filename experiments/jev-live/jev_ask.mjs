// Jev question pack: fast structured vote on urgencies + tactic + candidate score.
// Usage: node jev_ask.mjs '<compact state text>'
import { experimental_evaluate as evaluate } from 'ai';

const state = process.argv[2] || 'Day 1 Turn 1. Money 3000. Farmer at shed. All soil empty.';
const result = await evaluate({
  model: 'typesafe-ai/jev',
  state,
  questions: {
    water_urgent: {
      type: 'boolean',
      instructions: 'Any TODAY-planted crop unwatered that dies tonight if missed? Answer true only on immediate death risk.',
    },
    feed_urgent: {
      type: 'boolean',
      instructions: 'Any animal unfed 1 day+ and 1 day from escape (2 consecutive unfed days)?',
    },
    harvest_due: {
      type: 'boolean',
      instructions: 'Any mature crop past max-yield day or animal product ready that decays/loses value if skipped?',
    },
    tactic: {
      type: 'choice',
      instructions: 'Pick the single best tactic for THIS turn.',
      criteria: {
        feed: 'Feed hungry animals first (escape risk, care bonus needs fed+cared same day)',
        water: 'Water dry plants, TODAY-plants first (planting-day watering is mandatory)',
        harvest: 'Harvest mature crops/animal products before decay deadlines',
        build: 'Build pasture/coop so carried animals can be placed',
        place: 'Place carried animals onto empty structures',
        plant: 'Plant fixed footprint from seed stock before deadlines',
        market: 'Market first (hire/buy seeds/animals/feed buffer) to unblock the plan',
        move: 'Move toward target when nothing actionable on current cell',
      },
    },
    plan_quality: {
      type: 'score',
      instructions: 'Rate the proposed rule-based plan for this turn.',
      criteria: ['terrible', 'bad', 'ok', 'good', 'excellent'],
    },
  },
});
console.log(JSON.stringify({ answers: result.answers, usage: result.usage }));
