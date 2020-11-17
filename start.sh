#!/bin/bash
# automatisoidaan servun aloitusta, aluksi opetellaan pelkän botin kanssa.
# katsotaan jos botti päällä, niin sammutetaan eka ja sitten käynnistetään uusiksi

# botti tarvitsee enterin yhdistämiseen joten sen kanssa pitää erikseen sitten detachaa screeni
echo "old bots id:"
process=$(pidof -x python3 bot.py)
echo "killing old bot $process"
kill -TERM $process
echo "starting new bot"
screen -dm -S bottiscreeni pipenv run python3 bot.py
echo "botti aloitettu"

# screen -X screen -S bottiscreeni -t webbisivu 1
# samaan tapaan webbisivun kanssa paitti pitää tappaa npm ja node kummatkin
#npmid=$(pidof npm)
#nodeidlist=$(pidof node)
#echo "killing old web processes $npmid and $nodeid"
#kill -TERM $npmid
#for p in $nodeidlist
#    do
#        echo "killing $p"
#        kill -TERM $p
#done
#echo "opening new web"
# ei toimi tämä setti vielä
#screen -X screen -S bottiscreeni -t webbisivu 1 echo "kissa" # cd ../weekling-web/webfront npm start
#echo "webbi aloitettu"

# samaan tapaan sitten ngrok
#ngrokid=$(pidof ngrok)
#echo "killing ngrok tunnel $ngrokid"
#kill -TERM $ngrokid
#echo "opening new ngrok tunnel"
#screen -dm -S ngrokscreeni cd ../weekling-web/webback bash updateaddr.sh
#echo "ngrok aloitettu"
#
echo "everything rolling smoothly again.."
