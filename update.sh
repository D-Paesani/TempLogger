#git remote set-url origin git@github.com:D-Paesani/CRT-source.git
git add .
dt=`date '+%d/%m/%Y_%H:%M:%S'`
git commit -m $dt
git push -u origin main

