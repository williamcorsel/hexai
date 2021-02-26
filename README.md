# HexAIpy

Play Hex by yourself or against AI!

## Installation

Install dependencies easily using:

```bash
pip install -r requirements.txt
```

## How to run?

You can run the main program where you can play Hex against another (local) player or an AI using the following command:

```bash
python hexai.py
```

Optionally you can add the following flags:

|Option | Action | Choices | Default |
| --- | --- | --- | --- |
| -p1 | Choose Player 1 (Blue) type | {human, alphabeta, mcts} | human |
| -p2 | Choose Player 2 (Red) type | {human, alphabeta, mcts} | mcts |
| -s, --size | Specify board size | int | 4 |
| -t, --use_tt | Use transposition table | bool | False |
| -b, --begin | Which player starts the game (1/2) | int | 1 |

You can place Hex pieces by typing the coordinate when prompted. The coordinate should be contain a letter and a number to indicate the column and row (e.g., b3).

## Experiments

The accompanying report contains various experiments that were performed on the different AI variants. To perform the experiments yourself, use the `hexexperiments.py` file.

The following experiments have been performed:

### Alpha-Beta Comparison

Compares AB with a random evaluation function against AB's with the Dijkstra evaluation function: 

```
python hexexperiments.py comp -o base -m
```

### Iterative Deepening + Tranposition Table Comparison

Compares the IDTT agent against base AB agents:

```
python hexexperiments.py comp -o idtt -m
```

### Monte-Carlo Tree Search Optimisation

Compares different MCTS agents to find the optimal parameter settings

```
python hexexperiments.py mcts
```

This experiment takes about 17 minutes to complete on a 12-core AMD Ryzen 5900x processor. The processing time can be decreased by changing the values in the `n_options` and `cp_options` arrays or by lowering the number of matches played by using the `-n` flag.

### Monte-Carlo Tree Search Comparison

Compares the best MCTS agent against the IDTT agent

```
python hexexperiments.py comp -o mcts -m
```

### (More statistics)

The `exp_competition_old.py` file contains a singlethreaded implementation of the experiments returning some more statistics. You can run it using:

```
python hexexperiments.py comp_old
```

Warning: These experiments can take a long time as only a single thread is used!

### Other Experiment Flags

To play around more with the experiments, you can change the following flags:

|Option | Action | Choices | Default |
| --- | --- | --- | --- |
| \<test\> | Experiment type | {comp, comp_multi, mcts} | - |
| -o, --option | What agents are tested when using comp / comp_multi | {base, idtt, mcts} | base |
| -s, --size | Specify board size | int | 5 |
| -n, --no_matches | Manually specify number of matches | int | None |
| -m, --start_moves | Use predefined start moves | bool | False |