
# GNU Radio HW for ECSE351 - Interferometry. Ruslan Gindullin

## Overview

This is a fork of a GNU Radio Companion project. See the original [here](https://github.com/Jtearwicker/AGISETI/blob/main/Week4_Radio_Astronomy_II/grc_files/Interferometry.grc)

## GRC Flowgraph

The main flowgraph for this project is: `[Interferometry.grc]`


## Dependencies

*   GNU Radio (version 3.10.12 or later)

## Installation

1.  Install GNU Radio and its dependencies.
2.  Clone this repository:

    ```bash
    git clone https://github.com/ruslanbd/gnuradio.git
    cd gnuradio
    ```

## Usage

1.  Open the flowgraph `[flowgraph_name.grc]` in GNU Radio Companion.
2.  Execute the flowgraph.
3.  Input parameters of the system
4.  Observe changes on the graph


## Changes from the original flowgraph

- Two more antennas added, with their own signal parameters
- Additional entries for those antennas in the GUI
- The antennas' parameters are relative to antenna 1

This allows for setting up a 4-element linear phased antenna array by inputting the phases 360, 720, 1080 degrees for antennas 2, 3, and 4, respectively.

In theory, such a setup would allow for an increased signal gain in low SNR conditions, as the signal would add up coherently, while the noise would add up incoherently, increasing the apparent SNR after the summator. To model the noise difference, all four antennas have different noise RNG seeds. 

To see what the effect would be if the noise seeds were the same (all antennas in the same place), one could always change all seeds to be the same in the "Channel model" blocks. This will model a theoretical scenario when all antennas hear the same noise at the same time in the same place, but do not electromagnetically interfere with each other.
In this case, the noise floor should increase and we wouldn't get any SNR advantage from having multiple antennas.

## Contributing

Feel free to open issue on Github or create a pull request if you have an idea of how to improve on the project. You can also fork this repo.

## License

GNU GPLv3

## Author

Ruslan Gindullin, Case Western Reserve University '27, Electrical Engineering BSE student
