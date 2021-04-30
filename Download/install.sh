#!/bin/sh

#wget -q "--no-check-certificate" https://raw.githubusercontent.com/ziko-ZR1/FootOnsat/main/Download/install.sh -O - | /bin/sh

PLUGIN_PATH='/usr/lib/enigma2/python/Plugins/Extensions/FootOnSat'
DB_PATH='/usr/lib/enigma2/python/Plugins/Extensions/FootOnSat/db'
TMP_DB='/tmp/footonsat.db'

if [ -f /etc/apt/apt.conf ] ; then
    STATUS='/var/lib/dpkg/status'
    OS='DreamOS'
elif [ -f /etc/opkg/opkg.conf ] ; then
   STATUS='/var/lib/opkg/status'
   OS='Opensource'
fi

if [ -f $PLUGIN_PATH ]; then

    if [ -f '/usr/lib/enigma2/python/Plugins/Extensions/FootOnSat/db/footonsat.db' ]; then
        echo "Keep old db...."
        cp -a /usr/lib/enigma2/python/Plugins/Extensions/FootOnSat/db/footonsat.db /tmp
    fi

    echo "Remove old version."
    if [ $OS = "Opensource" ]; then
        opkg remove enigma2-plugin-extensions-footonsat
    else
       apt-get purge --auto-remove enigma2-plugin-extensions-footonsat
    fi

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

    if [ $OS = "Opensource" ]; then
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
    else
        echo "=========================================================================="
        echo "Some Depends Need to Be downloaded From Feeds ...."
        echo "=========================================================================="
        echo "apt Update ..."
        echo "========================================================================"
        apt-get update
        echo "========================================================================"
        echo " Downloading alsa-utils-aplay ......"
        apt-get install alsa-utils-aplay -y
        echo "========================================================================"
        echo "========================================================================"
        echo " Downloading $SQLITE3 , $PYSIX ......"
        apt-get install $SQLITE3 -y
        echo "========================================================================"
        apt-get install $PYSIX -y
        echo "========================================================================"
    fi


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

if [ $OS = "Opensource" ]; then
    wget "--no-check-certificate" "https://github.com/ziko-ZR1/FootOnsat/blob/main/Download/enigma2-plugin-extensions-footonsat_1.1_all.ipk?raw=true" -O "/tmp/enigma2-plugin-extensions-footonsat_1.1_all.ipk";
    opkg install /tmp/enigma2-plugin-extensions-footonsat_1.1_all.ipk
    rm -f /tmp/enigma2-plugin-extensions-footonsat_1.1_all.ipk
else
    wget "--no-check-certificate" "https://github.com/ziko-ZR1/FootOnsat/blob/main/Download/enigma2-plugin-extensions-footonsat_1.1.deb?raw=true" -O "/tmp/enigma2-plugin-extensions-footonsat_1.1.deb";
    dpkg -i --force-overwrite /tmp/enigma2-plugin-extensions-footonsat_1.1.deb; apt-get install -f -y
    rm -f /tmp/enigma2-plugin-extensions-footonsat_1.1.deb
fi

if [ -f $PLUGIN_PATH  ]; then
    if [ -f $TMP_DB ]; then
        cp -a $TMP_DB $DB_PATH
        rm -f $TMP_DB
    fi
fi

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
