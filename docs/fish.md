# How do Fish work?

Here, I'll outline how the `Fish` class behavior is implemented.
This is not documentation about the class itself but rather a higher level overview
of how different stats like `health`, `hunger`, `happiness`, etc. are implemented, and
how the fish chooses to act!

## Stats

Many of these stats are modeled as continuous ODEs. The time component is the delta time between 
each loop, so it's discretized, but it's fine. We do some math to ensure that the the time component is in seconds, so all the rates are in unts of 1/s.

All of these stats are in the range [0, 1], regardless of different fishes.

### Health

d`health`/dt = +((0.5 - `hunger`) * `starvation_rate`) + ((0.5 - `happiness`) * `happiness_health_rate`)

### Hunger

d`hunger`/dt = +`hunger_rate` * `speed` * `width`

### Happiness

`happiness` is the sum of the following factors:

- The total sum of `relationships` scores of all online users

- `hunger_happiness_bonus` * (1 - `hunger`)

- `health_happiness_bonus` * `health`