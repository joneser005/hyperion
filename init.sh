#!/usr/bin/env bash
# Prepares the file system and motion.conf settings.
# hyperion.py defaults assumed to match this file, else you must adjust accordingly.
#
# Edit this file to suit your environment.

usermod -a -G users motion -d /home/motion

sed -i 's/^daemon off/daemon on/' /etc/motion/motion.conf
sed -i 's/^width.*/width 640/' /etc/motion/motion.conf
sed -i 's/^height.*/height 480/' /etc/motion/motion.conf
sed -i 's/^framerate.*/framerate 2/' /etc/motion/motion.conf
sed -i 's/^minimum_frame_time.*/minimum_frame_time 3/' /etc/motion/motion.conf
sed -i 's/^target_dir.*/target_dir \/var\/lib\/motion/' /etc/motion/motion.conf
sed -i 's/^[ ]*(;|#)*[ ]*on_event_start.*/on_event_start echo \'Started\'' >> \/home\/motion\/on_event_start/' /etc/motion/motion.conf
sed -i 's/^[ ]*(;|#)*[ ]*on_motion_detected.*/on_motion_detected python3 \/home\/motion\/hyperion.py/' /etc/motion/motion.conf
