# Chibi Robo Setup Guide

## Required Software

- Archipelago Build of Chibi Robo from: [Chibi-Robo: Plug Into Adventure AP World](https://github.com/EverydaySimpleDev/Archipelago)
- Chibi Robo: Unplugged from: [Chibi-Robo: Unplugged Randomization App](https://github.com/EverydaySimpleDev/Chibi-Robo-Randomizer)

## Optional Software
- Chibi Robo: Emo / PopTracker pack from: [Tracker Pack](https://github.com/EverydaySimpleDev/EmoTrackerPacks)

## Installation Procedures (Windows)

1. Download the above release and extract it.
2. Generate your world and extract the zip file
3. Location the .apcr file from the zip
4. Use the Chibi Robo Randomizer to randomize your game

## Joining a MultiWorld Game

1. After using the Chibi Robo Rando application launch the Chibi Robo Client
   - You can now have the AP app open the .apcr file to auto open the current client
2. The client will autodetect your player info and connect to the server
   - Make sure you are already loaded into your save file before you try to connect the game to the server

## Troubleshooting

If the client can't connect to Dolphin, type `/dolphin` in the client to see why, then check the following:

- In Dolphin, make sure `Enable Emulated Memory Size Override` (under `Options` > `Configuration` > `Advanced`) is
  **disabled**. The game has to be closed to change it. 
- Start the randomized game in Dolphin before connecting, and wait until Chibi Robo is actually running, not just
  the Dolphin game list or the GameCube boot menu.
- Only the NTSC-U version of Chibi Robo (game ID `GGTE01`) is supported. You can check the game ID in Dolphin's
  game list. A randomized PAL or Japanese ISO will run, but the client won't connect to it.
- Run Dolphin and the Archipelago Launcher the same way: both normally, or both as administrator. Running only one
  of them as administrator stops the client from reading the game.