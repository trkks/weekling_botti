#!/bin/bash

# automatisoidaan servun aloitusta

# tuhotaan vanha tmux sessio, ja näin sen alla toimivat prosessit, kuten botti, webbisivu ja ngrok-tunneli.
tmux kill-server
# pkill -f tmux # ilman tmuxin käyttöä


# tapetaan vanhat prosessit, botti, webbisivu ja ngrok tunneli
process=$(pidof -x python3 bot.py)
kill -TERM $process

npmid=$(pidof npm)
nodeidlist=$(pidof node)
kill -TERM $npmid
for p in $nodeidlist
    do
        kill -TERM $p
done

ngrokid=$(pidof ngrok)
kill -TERM $ngrokid

# aloitetaan tmux pääsessio nimeltä botti
tmux new-session -d -s botti
tmux rename-window 'wkbot'

# käynnistetään botti
tmux send-keys 'pipenv run python3 bot.py' C-m

# splitataan alaterminaali jossa ruvetaan ajaan nettisivua
tmux split-window -h bash
tmux send-keys 'cd ../weekling-web/webfront ; npm start' C-m

# splitataan toinen alaterminaali jossa ruvetaan ajaan ngrok-tunnelia
tmux split-window -h bash
tmux send-keys 'cd ../weekling-web/webback ; bash updateaddr.sh' C-m

# detachataan näistä
tmux -2 attach-session -d

# smooth operatoor..
