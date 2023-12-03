#!/bin/bash
PATH=/usr/local/bin:/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/home/hep/.local/bin:/home/hep/bin

# Specify the path to your conda installation (modify as needed)
CONDA_PATH="/home/hep/miniforge3/"

# Specify the name of the conda environment
ENV_NAME="slowcontrol"

# Activate the conda environment


conda activate "${ENV_NAME}"
source ~/conda_init.sh
source "${CONDA_PATH}/etc/profile.d/conda.sh"
conda activate "${ENV_NAME}"
which python
while true; do
cd /home/hep/PycharmProjects/pythonProject/runze/UCSB_TS_slowcontrol
#source /home/hep/PycharmProjects/SBC_slowcontrol_test/clear_tcp.sh
#/hep/home/miniforge3/envs/sbcslowcontrol/bin/python /home/hep/PycharmProjects/SBC_slowcontrol_test/PLC.py
source ./clear_tcp.sh
python ./SC_BKG.py
sleep 2
done
echo "quit the loop" > ~/ECHO.txt
