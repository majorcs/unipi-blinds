#!/bin/bash

# 2.02: Haloerkely FEL
# 2.03: HaloErkely LE
# 2.04 MarciErkely FEL
# 2.05 MarciErkely LE
# 2.06 Dolgozo2 LE
# 2.07 Dolgozo2 FEL
# 2.09 MarciAblak LE
# 2.10 MarciAblak FEL
# 2.11 DomiAjto LE
# 2.12 DomiAjto FEL
# 2.13 DomiAblak FEL
# 2.14 DomiAblak LE
# 3.02 KonyaAbalak2 LE
# 3.03 KonyaAbalak2 FEL
# 3.04 KonhyhaAblak3 FEL
# 3.05 KonhyhaAblak3 LE
# 3.06 KonyhaAblak1 FEL
# 3.07 KonyhaAblak1 LE
# 3.09 HaloAblak1 LE
# 3.10 HaloAblak1 FEL
# 3.11 HaloAblak2 FEL
# 3.12 HaloAblak2 LE
# 3.13 Dolgozo1 FEL
# 3.14 Dolgozo1 LE

RELE_LE=(2_03 2_05 2_06 2_09 2_11 2_14 3_09 3_12 3_14)
RELE_FEL=(2_02 2_04 2_07 2_10 2_12 2_13 3_10 3_11 3_13)

if [ "$1" = "FEL" ]
then
	IRANY=(${RELE_FEL[*]})
else
	IRANY=(${RELE_LE[*]})
fi

for RELE in ${IRANY[*]}
do
	curl --request POST --url "http://192.168.88.32:8080/rest/relay/$RELE" --data 'mode=simple&value=1'
	echo
done

sleep 30

for RELE in ${IRANY[*]}
do
	curl --request POST --url "http://192.168.88.32:8080/rest/relay/$RELE" --data 'mode=simple&value=0'
	echo
done

