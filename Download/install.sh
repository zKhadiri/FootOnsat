#!/bin/sh

#wget -q "--no-check-certificate" http://raw.githubusercontent.com/ziko-ZR1/FootOnsat/main/Download/install.sh -O - | /bin/sh


if [ -f /etc/apt/apt.conf ] ; then
    	echo "#########################################################"
	echo "#       this image is not supported                     #"
	echo "#########################################################"
    exit 1
elif [ -f /etc/opkg/opkg.conf ] ; then
   STATUS='/var/lib/opkg/status'
fi

if [ -d /usr/lib/python3.8 ] ; then
   echo "Python3"
   PYTHON='PY3'
   SQLITE3='python3-sqlite3'
   PYSIX='python3-six'
else
   echo "Python2"
   PYTHON='PY2'
   SQLITE3='python-sqlite3'
   PYSIX='python-six'
fi

if grep -q $SQLITE3 $STATUS; then
    sqlite='Installed'
fi

if grep -q $PYSIX $STATUS; then
    six='Installed'
fi

if grep -q 'alsa-utils-aplay' $STATUS; then
    aplay='Installed'
fi

if [ $sqlite = "Installed" -a $six = "Installed" -a $aplay = "Installed" ]; then
     echo ""
else
    echo "=========================================================================="
    echo "Some Depends Need to Be downloaded From Feeds ...."
    echo "=========================================================================="
    echo "Opkg Update ..."
    echo "========================================================================"
    opkg update
    echo "========================================================================"
    echo " Downloading alsa-utils-aplay ......"
    opkg install alsa-utils-aplay
    echo "========================================================================"
    echo "========================================================================"
    echo " Downloading $SQLITE3 , $PYSIX ......"
    opkg install $SQLITE3
    echo "========================================================================"
    opkg install $PYSIX
    echo "========================================================================"


fi

if grep -q 'alsa-utils-aplay' $STATUS; then
	echo ""
else
	echo "#########################################################"
	echo "#       alsa-utils-aplay Not found in feed              #"
	echo "#  Notification sound will not work without alsa aplay  #"
	echo "#########################################################"
fi

if grep -q $SQLITE3 $STATUS; then
	echo ""
else
	echo "#########################################################"
	echo "#       $SQLITE3 Not found in feed                      #"
	echo "#########################################################"
    exit 1
fi

if grep -q $PYSIX $STATUS; then
	echo ""
else
	echo "#########################################################"
	echo "#       $PYSIX Not found in feed                        #"
	echo "#########################################################"
    exit 1
fi

wget "--no-check-certificate" "https://github.com/ziko-ZR1/FootOnsat/blob/main/Download/enigma2-plugin-extensions-footonsat_1.0_all.ipk?raw=true" -O "/tmp/enigma2-plugin-extensions-footonsat_1.0_all.ipk";

opkg install /tmp/enigma2-plugin-extensions-footonsat_1.0_all.ipk

echo ""
echo "#########################################################"
echo "#          FootOnsat INSTALLED SUCCESSFULLY             #"
echo "#                BY ZIKO  & Redouane                    #"
echo "#########################################################"
echo "#                Restart Enigma2 GUI                    #"
echo "#########################################################"
sleep 2
killall -9 enigma2
exit 0
