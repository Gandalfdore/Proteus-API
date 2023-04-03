
# Proteus Scripts

API and example code for work with the Proteus P9484M (all in one AWG from Tabor Inc.)

## Preliminary requirements 

- Python 3.8 and above.
- Jupter Enviroment.


## Installation

Clone the repository into your local machine and open the \Notebooks\Signal_generation\EXAMPLE.ipynb with jupyter notebook or lab. Follow the notebook's guidance.


## Table of Contents

### Sample code, to demonstrate the execution of the device's capabilities (especially for quantum computing applications), this would inculde:

* Device initializations

* Defintion of pulses for quantum control
	* Cos packet pulse
	* Gaussian pulse
	* DRAG pulse
	* Simple sinusoid pulse
	* Rabi pulse
	* Readout pulse (for now it is the same as the Rabi pulse)

* Task tables to manipulte the sequence of pulses and their triggering/synchronization

* Signal generation with the AWG module

* Readout with the Digitizer + ADC module


### The libraries (located in SourceFiles) are separated in two parts:

* Libraries written by yours truly for the quantum computing purposes (these define the API):
	* initializers
	* tasks
	* pulse_lib
	* helpers
	* readers

* Libraries taken from the manifacturer Tabor Inc. (https://github.com/pgwijesinghe/taborelec-proteusawg-new)
(these are the drivers for the device) under GPL license:

	* pyte_visa_utils
	* tep_interleaved_wave
	* tep_task_table
	* tevisainst
	* teproteus




## License

[GPL](https://www.gnu.org/licenses/gpl-3.0.html)
