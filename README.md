# SCPI LAN Generators

A Python application for controlling test and measurement equipment (generators) using SCPI commands over a LAN connection.

## Description

This project provides a command-line interface to interact with signal generators and other instruments that support the Standard Commands for Programmable Instruments (SCPI) protocol. It allows users to send commands, query instrument status, and automate testing procedures.

## Features

*   Connect to instruments over a LAN network.
*   Send SCPI commands to control instrument settings.
*   Read responses from instruments.
*   Configure connection settings via a `config.csv` file.

## Requirements

*   Python 3.x
*   pyvisa
*   pyvisa-py

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/your-username/SCPI_LAN_generators.git
    ```
2.  Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: A `requirements.txt` file may need to be created if one does not already exist)*

## Usage

Run the application from the command line:

```bash
python main.py
```

Or, if you are on Windows, you can run the executable:

```bash
main.exe
```

## Configuration

The `config.csv` file is used to configure the connection to the instrument. The file should contain the following columns:

*   `IP`: The IP address of the instrument.
*   `Port`: The port number for the connection.
*   `Timeout`: The connection timeout in milliseconds.
*   `Instrument`: The name or model of the instrument.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
