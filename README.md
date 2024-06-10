# CLI-board-manager

CLI-board-manager is a clipboard manager for the terminal written in Python with the ✨awesome✨ [Textual](https://www.textualize.io) framework.

## Features

### Keeping track of clipboard history

CLI-board-manager keeps track of all items you place on the clipboard using the normal copy action. If you accidentally copy sensitive information, press the Delete button for that item to remove it from the interface _and_ the clipboard.

![Screenshot showing the clipboard history](https://github.com/davidfokkema/cli-board-manager/raw/main/images/screenshot-history.png)

### Create copy/paste workflows

Filling out a series of web forms or sending messages with a subject field and a body can be tiresome if you don't have a clipboard manager. With CLI-board-manager workflows you can select clipboard items and add them to the workflow tab. If you start a workflow the first item is put on the clipboard, e.g. the subject field. You can then paste that field and switch back to the app. The moment the app becomes active, it automatically puts the next item on the clipboard, e.g. the body of your message. Switch back to your message and paste the body. If you reach the end of your workflow, CLI-board-manager will automatically loop back to the first item, until you stop the workflow.

If you make a mistake and need to move to another item in the workflow, just select that item and the workflow will continue there.

![Screenshot showing the clipboard history](https://github.com/davidfokkema/cli-board-manager/raw/main/images/screenshot-workflow.png)

## Usage

Run the `cbm` command from the terminal, after installation. Use your mouse to navigate the interface or use a combination of the Tab and arrow keys along with any keyboard shortcuts indicated in the footer. Click on old items to copy them to the clipboard or press enter after selecting with the arrow keys.

## Installation

This is a Python app and currently not distributed stand-alone using a nice installer. So you'll need to have Python installed and some basic knowledge about installing Python packages. [Pipx](https://pipx.pypa.io/stable/) is, in most cases, the preferred method of installation.

### Using pipx

Just run
```shell
pipx install cli-board-manager
```

### Using pip

Preferably in a new virtual environment, run
```shell
pip install cli-board-manager
```

### From source, using Poetry

Clone the [repository](https://github.com/davidfokkema/cli-board-manager), cd into the repository's main directory and run
```shell
poetry install
```

## Copyright and License

Copyright (C) 2024 David Fokkema

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.