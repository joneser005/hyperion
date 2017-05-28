#!/bin/bash
echo 'motion-detected.sh started' | tee -a /home/motion/log/motion.log
python3 /home/motion/hyperion.py -l /home/motion/log/hyperion.log -p /home/motion/.secret -s /home/motion/.stamp | tee -a /home/motion/log/motion.log

