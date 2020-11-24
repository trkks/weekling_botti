#!/bin/bash
# automatisoidaan servun aloitusta, aluksi opetellaan pelkän botin kanssa.
# katsotaan jos botti päällä, niin sammutetaan eka ja sitten käynnistetään uusiksi
# echot jää nyt johkin kauas piiloon tmuxin takia. eipä se haittaa.

# tapetaan vanha tmux sessio, periaatteessa kai tuhoaa myös muutkin, joten alla oleva turhaa? TODO: testaa tämä
tmux kill-server
# pkill -f tmux # ilman tmuxin käyttöä
# tapetaan vanha botti, vanhat webbisivut ja ngrok tunneli
process=$(pidof -x python3 bot.py)
echo "killing old bot $process"
kill -TERM $process

npmid=$(pidof npm)
nodeidlist=$(pidof node)
echo "killing old web processes $npmid and $nodeid"
kill -TERM $npmid
for p in $nodeidlist
    do
        echo "killing $p"
        kill -TERM $p
done

ngrokid=$(pidof ngrok)
echo "killing ngrok tunnel $ngrokid"
kill -TERM $ngrokid

echo "starting new bot"
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

echo "everything rolling smoothly again.."
