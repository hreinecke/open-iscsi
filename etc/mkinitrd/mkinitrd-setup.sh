#!/bin/bash
#
#%stage: device
#
check_iscsi_root() {
    local devname=$1
    local sysfs_path

    sysfs_path=$(/sbin/udevadm info -q path -n $devname 2> /dev/null)
    if [ -z "$sysfs_path" ] ; then
	sysfs_path="/block${devname##/dev}"
    fi
    if [ ! -d /sys$sysfs_path ] ; then
	return;
    fi

    pushd /sys$sysfs_path > /dev/null
    if [ ! -d device ] ; then
	cd ..
    fi

    if [ ! -d device ] ; then
	# no device link; return
	popd > /dev/null
	return;
    fi

    cd -P device
    cd ../..

    if [ -d connection* ]; then
	cd -P connection*
	cid=${PWD#*connection}
	sid=${cid%%:*}
	if [ -d /sys/class/iscsi_session/session$sid ]; then
	    cd -P /sys/class/iscsi_session/session$sid
	    echo $(basename $PWD)
	fi
    fi
    popd > /dev/null
}

for bd in $blockdev; do
    update_blockdev $bd
    sid=$(check_iscsi_root $bd)
    if [ "$sid" ]; then
    	root_iscsi=1
    	iscsi_sessions="$iscsi_sessions ${sid#session}"
    fi
done

save_var root_iscsi
save_var iscsi_sessions

if [ "${root_iscsi}" ]; then
    for session in $iscsi_sessions; do
	eval TargetName${session}=$(cat /sys/class/iscsi_session/session${session}/targetname)
	eval TargetAddress${session}=$(cat /sys/class/iscsi_connection/connection${session}:0/address)
	eval TargetPort${session}=$(cat /sys/class/iscsi_connection/connection${session}:0/port)

	save_var TargetName${session}
	save_var TargetAddress${session}
	save_var TargetPort${session}
    done
    # copy the iscsi configuration
    cp -rp /etc/iscsi etc/
    # Use default interface
    interface="default"

    save_var TargetPort 3260 # in case the port was not defined via command line we assign a default port
fi
