import copy
import os
import threading
import time

import PySimpleGUI as sg


# the main page consists of 2 button, one is config, another is start
# press config to show configBox, press start to show startBox
def showMainPage():
    main = sg.Window("Main", [[sg.Button("Config", key='-CONFIG-')], [sg.Button("Start", key='-START-')]])
    while True:
        event, values = main.read()
        if event == sg.WIN_CLOSED:
            break
        if event == '-CONFIG-':
            showConfigBox()
        if event == '-START-':
            showStartBox()
    main.close()


CONFIG: dict = {
    "limit": False,
    "numplayers": "3",
    "numrounds": "4",
    "blind": "50 100 0",
    "firstplayer": "3 1 1 1",
    "numsuits": "4",
    "numranks": "13",
    "numholecards": "2",
    "numboardcards": "0 3 1 1",
    "stack": "20000 20000 20000",
    "raisesize": "10 10 20 20",
    "maxraises": ""
}


# load config in './config.game'
def loadConfig(conf: dict):
    f = open("./config.game", "a+")
    config = f.readlines()
    f.close()
    for line in config:
        line = line.strip()
        if (len(line) < 2) or (line[0] == '#'):
            continue
        if line == "GAMEDEF":
            continue
        if line == "nolimit":
            conf["limit"] = False
            continue
        if line == "limit":
            conf["limit"] = True
            continue
        if line == "END GAMEDEF":
            break
        line = line.split("=")
        conf[line[0]] = line[1]


# save config to './config.game'
def saveConfig(conf):
    f = open("./config.game", "w")
    f.write("GAMEDEF\n")
    if conf["limit"]:
        f.write("limit\n")
    else:
        f.write("nolimit\n")
    for key in conf:
        if key == "limit":
            continue
        if (conf[key] == "") or (conf[key] == " "):
            continue
        if (conf["limit"]) and (key == "stack"):
            continue
        if (not conf["limit"]) and (key == "raisesize"):
            continue
        f.write(key + "=" + conf[key] + "\n")
    f.write("END GAMEDEF\n")
    f.close()


# show the box to input config
def showConfigBox():
    config = copy.deepcopy(CONFIG)
    loadConfig(config)
    configBox = sg.Window("Config", [
        [sg.Text("Limit")],
        [sg.Checkbox("Limit", key='limit', default=config['limit'])],
        [sg.Text("NumPlayers \t (the number of players)")],
        [sg.InputText(key='numplayers', default_text=config['numplayers'])],
        [sg.Text("NumRounds \t (the number of rounds)")],
        [sg.InputText(key='numrounds', default_text=config['numrounds'])],
        [sg.Text("Blind    \t (the blind of each player)")],
        [sg.InputText(key='blind', default_text=config['blind'])],
        [sg.Text("FirstPlayer \t (the first player of each round)")],
        [sg.InputText(key='firstplayer', default_text=config['firstplayer'])],
        [sg.Text("NumSuits \t (the number of different suits in the deck)")],
        [sg.InputText(key='numsuits', default_text=config['numsuits'])],
        [sg.Text("NumRanks \t (the number of different ranks in the deck)")],
        [sg.InputText(key='numranks', default_text=config['numranks'])],
        [sg.Text("NumHoleCards \t (the number of private cards to deal to each player)")],
        [sg.InputText(key='numholecards', default_text=config['numholecards'])],
        [sg.Text("NumBoardCards \t (the number of cards revealed of each round)")],
        [sg.InputText(key='numboardcards', default_text=config['numboardcards'])],
        [sg.Text("Stack    \t (the stack of each player, only for no-limit games)")],
        [sg.InputText(key='stack', default_text=config['stack'])],
        [sg.Text("RaiseSize \t (the size of raises on each round, only for limit games)")],
        [sg.InputText(key='raisesize', default_text=config['raisesize'])],
        [sg.Text("MaxRaises \t (the maximum number of raises on each round, optional)")],
        [sg.InputText(key='maxraises', default_text=config['maxraises'])],
        [sg.Button("OK", key='-OK-'), sg.Button("Cancel", key='-CANCEL-')]
    ], resizable=True, font=('Helvetica', 15), element_padding=(5, 5))
    while True:
        event, values = configBox.read()
        if event == sg.WIN_CLOSED:
            break
        if event == '-OK-':
            config.update(values)
            saveConfig(config)
            break
        if event == '-CANCEL-':
            break
    configBox.close()


# show the box to start the game
# the number of players is defined in 'numplayers' in the file './config.game'
def showStartBox():
    if not os.path.exists("./config.game"):
        sg.popup("Please set the config first!")
        return
    config = copy.deepcopy(CONFIG)
    loadConfig(config)
    numplayers = int(config['numplayers'])
    playersInput = [[sg.InputText(key='player' + str(i + 1) + ' name', default_text='player' + str(i + 1) + 'name')]
                    for i in range(numplayers)]
    playersExec = [[sg.InputText(key='player' + str(i + 1) + ' exec', default_text='example_player')]
                   for i in range(numplayers)]
    playersText = [[sg.Text("Player" + str(i + 1) + " name")] for i in range(numplayers)]
    playersExecText = [[sg.Text("Player" + str(i + 1) + " exec")] for i in range(numplayers)]

    combined = [[sg.Text("Game Name")],
                [sg.InputText(key='game name', default_text='TestGame')],
                [sg.Text("Game Times")],
                [sg.InputText(key='game times', default_text='1000')]]
    for i in range(numplayers):
        combined.append(playersText[i])
        combined.append(playersInput[i])
        combined.append(playersExecText[i])
        combined.append(playersExec[i])
    combined.append([sg.Button("START", key='-START-'), sg.Button("Cancel", key='-CANCEL-')])
    startBox = sg.Window("Start", combined, resizable=True, font=('Helvetica', 15), element_padding=(5, 5))
    while True:
        event, values = startBox.read()
        if event == sg.WIN_CLOSED:
            break
        if event == '-START-':
            # check if there is 'config.game'
            cmd = "./dealer " + values['game name'] + " ./config.game " + values['game times'] + " 0"
            for i in range(numplayers):
                cmd += " " + values['player' + str(i + 1) + ' name']
            cmd += " > log.txt"
            # run cmd in thread
            t = threading.Thread(target=os.system, args=(cmd,))
            t.start()
            time.sleep(1)
            # read the ports from the log file
            f = open("log.txt", "r")
            ports = f.readline().split(" ")
            f.close()
            # start the player
            for i in range(numplayers):
                cmd = "./" + values['player' + str(i + 1) + ' exec'] + " config.game localhost " + ports[i]
                ti = threading.Thread(target=os.system, args=(cmd,))
                ti.start()
            # wait until t is finished
            t.join()
            f = open("log.txt", "r")
            score = f.readlines()[-1]
            sg.popup(score, title="Score", font=('Helvetica', 15))
            break
        if event == '-CANCEL-':
            break
    startBox.close()


if __name__ == "__main__":
    sg.theme('Tan')
    showMainPage()
