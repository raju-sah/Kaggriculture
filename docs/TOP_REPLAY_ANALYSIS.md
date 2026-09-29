# Top-agent public replay analysis

Source video: `/home/raju/Videos/Screencasts/Screencast from 2026-09-20 08-36-02.mp4`.
The recording identified public episode `111058336`, seed `501279899`, between
Majkel1337 and DSM. The Kaggle CLI replay is a stronger source than pixel
inference because it contains every public action and observation. The replay
uses `kaggriculture` module `1.32.7` and ended 108,617 to 108,499.

Five recent direct matches between the same active top submissions were
profiled: `111021281`, `111036531`, `111047335`, `111052856`, and `111058336`.
Their seeds were respectively 176354738, 1199630878, 62921538, 666493463, and
501279899. Final coins ranged from 70,854 to 134,497. Raw replays are kept out
of Git; reproduce them with `kaggle competitions replay EPISODE_ID -p PATH` and
profile them with `python -m analysis.public_replay_profile PATH/*.json`.

## Repeated opening

Both agents use an almost identical opening in every sampled regime:

- Day 0 ends near 5 coins with four hands, two cows, three sheep, five
  pastures, 10 wheat tiles, and six melon tiles.
- Day 3 has 20 crop tiles; melon reaches 12 while wheat is converted into the
  first strawberry tiles.
- Day 5 has six hands, 12 melon, eight strawberry, and the original five
  animals.
- Day 6 buys the second quadrant and jumps to eight hands. The roster expands
  according to the realized demand regime.
- Day 9 buys the third quadrant, reaches 10 hands, and runs roughly 53–59 crop
  tiles. No sampled agent needed the fourth quadrant.
- Day 12 reaches about 11 hands and 58–61 crop tiles. Strawberry is normally
  the dominant cash crop, while wheat supplies feed and is also sold.

This is a qualitatively different capital schedule from the current champion.
The top opening spends to almost zero immediately, but avoids the old scale
clone's escape spiral through four starting hands, dense feed production,
continuous bought-feed fallback, and explicit task ownership.

## Adaptive allocation

The day-0 core is stable; the day-6 and later roster responds to demand:

- A milk-heavy season reached 14–15 cows and sold 351–362 milk per agent.
- A yarn-heavy season reached 10 sheep by day 9 and sold 258–267 wool.
- Mixed strawberry/milk seasons used about 9–11 cows, three sheep, and two
  geese. Egg output was about 81–84 when geese were selected.
- One weak-milk season shifted later capacity toward carrots, tomatoes, wheat,
  and sheep rather than continuing to add cows.

The agents react to realized prices and unlocked shops rather than treating one
day-3 shop as the whole-season policy. Eggs are a small stabilizer. Cows and
sheep are the main scalable animal branches.

## Production and market behavior

Across the five matches an agent bought 160–335 wheat while simultaneously
growing and selling 394–756 wheat. Bought feed is therefore a reliability
backstop, not a replacement for feed plots. Agents sold continuously instead
of carrying large inventories. Per-agent season totals included 177–289
fertilizer, 59–267 wool, 85–362 milk, 71–345 strawberry, and a fixed 72 melon
in most runs. Later crop space rotates from strawberry toward carrots and
tomatoes when their relative prices improve.

The replay shows why the current 45k design is capped: it has too little labor,
land, feed throughput, and product diversity. Small goose timing changes cannot
close a 60k-plus gap.

## Next experiment

Exp-0044 should reproduce only the shared opening first, through day 6:

1. Match the day-0 target of four hands, two cows, three sheep, five pastures,
   10 wheat, and six melon without escapes or rejected aggregate plant orders.
2. Match day-5 crop conversion to 12 melon and eight strawberry.
3. Add the second quadrant and eight-hand labor budget on day 6.
4. Stop there initially and measure whether the opening is reproducible across
   seeds, both seats, and the scale-opponent panel.

Only after the opening is stable should later modules add the third quadrant,
price-driven cow/sheep allocation, 50-plus crop scheduling, bought-feed
fallback, fertilizer routing, and continuous selling. Each stage needs replay
invariants for animal escapes, accepted plant counts, care/feed coverage,
travel, and cash floors. Copying a single seed's later actions would overfit;
the repeated opening and cross-seed allocation rules are the transferable
evidence.
