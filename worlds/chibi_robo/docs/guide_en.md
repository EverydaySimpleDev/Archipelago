# Chibi Robo Setup Guide

## Required Software
- Archipelago Build of Chibi Robo from: [Chibi Robo Archipelago Releases Page](https://github.com/PoryGoneDev/Celeste64/releases/)

## Installation Procedures (Windows)

1. Download the above release and extract it.

## Installation Procedures (Linux and Steam Deck)

1. Download the above release and extract it.

2. Add .exe to Steam as a Non-Steam Game. In the properties for it on Steam, set it to use Proton as the compatibility tool. Launch the game through Steam in order to run it.

## Joining a MultiWorld Game

1. Before launching the game, edit the `AP.json` file in the root of the Celeste 64 install.

2. For the `Url` field, enter the address of the server, such as `archipelago.gg:38281`. Your server host should be able to tell you this.

3. For the `SlotName` field, enter your "name" field from the yaml or website config.

4. For the `Password` field, enter the server password if one exists; otherwise leave this field blank.

5. Save the file, and run `.exe`. If you can continue past the title screen, then you are successfully connected.

An Example `AP.json` file:

```
{
	"Url": "archipelago.gg:12345",
	"SlotName": "Maddy",
	"Password": ""
}
```
