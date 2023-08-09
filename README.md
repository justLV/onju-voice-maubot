# 🤖 Maubot plugin for Onju Voice 🍐🔊
This is a maubot plugin for exposing new messages from Beeper on a local server, to be used with the demo code [here](https://github.com/justLV/onju-voice).

I've included everything that one should need to get a standalone Maubot plugin running with E2E encyption in this repo, assuming one has Beeper access, hopefully saving some of the typical pains.

My preference was to use the maubot install in standalone mode using a Conda environment and kept open in a tmux session, but you're free to modify to have this as a docker container for better restart handling.

## Usage

```
conda env create -f mb.yml
conda activate mb
```

To simplify the installation, I've included a script that logs in using `matrix-nio[e2e]` to create the device ID, access token, etc. 

Run the following (with conda env activated):

```
python initialize.py
```

Add your Beeper username (without :beeper.com) and password when prompted. This then sets up the `maubot.yaml` for Maubot to use.

As Maubot doesn't seem to be able to retrieve the useful info from Beeper rooms for descriptive formatting, this script also fetches that info and adds it to a json dict that to be referenced by Maubot.

This also means you'll need to re-run this script to index rooms from new senders from time to time. I'm sure there's a better way to do this in future, but this should be easy as it saves your access token so you don't need to login manually again.

Enter a `tmux` session if you want to detach and leave it running, and run the following to launch the Maubot plugin:

```
python -m maubot.standalone
```

This exposes a local API for fetching and sending messages.

You'll need to verify this device from the Beeper client.

If you are having issues getting messages from rooms with e2ee, you may need to remove the integration and re-add it while your plugin is running, and keys should then be automatically setup properly.
