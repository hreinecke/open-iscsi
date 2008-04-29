/*
 * iSCSI sysfs
 *
 * Copyright (C) 2006 Mike Christie
 * Copyright (C) 2006 Red Hat, Inc. All rights reserved.
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published
 * by the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 * General Public License for more details.
 */
#ifndef ISCSI_SYSFS_H
#define ISCSI_SYSFS_H

#include <sys/types.h>

#include "types.h"
#include "iscsi_proto.h"
#include "config.h"

struct iscsi_session;
struct iscsi_conn;
struct iscsi_session_operational_config;
struct iscsi_conn_operational_config;
struct iscsi_auth_config;

#define SCSI_MAX_STATE_VALUE 32

struct session_info {
	struct list_head list;
	/* local info */
	struct iface_rec iface;
	int sid;

	/* remote info */
	char targetname[TARGET_NAME_MAXLEN + 1];
	int tpgt;
	char address[NI_MAXHOST + 1];
	int port;
	char persistent_address[NI_MAXHOST + 1];
	int persistent_port;
};

struct host_info {
	struct iface_rec iface;
	int host_no;
};

extern int direntcmp(const void *d1, const void *d2);
extern void free_transports(void);
extern int get_iscsi_kernel_version(char *buf);
extern int check_class_version(void);
extern int get_sessioninfo_by_sysfs_id(struct session_info *info,
				      char *sys_session);
extern int sysfs_session_has_leadconn(uint32_t sid);

typedef int (sysfs_session_op_fn)(void *, struct session_info *);
typedef int (sysfs_host_op_fn)(void *, struct host_info *);

extern int sysfs_for_each_session(void *data, int *nr_found,
				  sysfs_session_op_fn *fn);
extern int sysfs_for_each_host(void *data, int *nr_found, sysfs_host_op_fn *fn);
extern uint32_t get_host_no_from_sid(uint32_t sid, int *err);
extern uint32_t get_host_no_from_iface(struct iface_rec *iface, int *rc);
extern char *get_blockdev_from_lun(int hostno, int target, int sid);
extern int set_exp_statsn(struct iscsi_conn *conn);

static inline int is_valid_operational_value(int value)
{
	return value != -1;
}

extern void get_auth_conf(int sid, struct iscsi_auth_config *conf);
extern void get_negotiated_session_conf(int sid,
				struct iscsi_session_operational_config *conf);
extern void get_negotiated_conn_conf(int sid,
				struct iscsi_conn_operational_config *conf);
extern pid_t scan_host(int hostno, int async);
extern int get_session_state(char *state, int sid);
extern int get_host_state(char *state, int host_no);
extern int get_device_state(char *state, int host_no, int target, int lun);
extern void set_device_online(int hostno, int target, int lun);
extern void delete_device(int hostno, int target, int lun);
extern void rescan_device(int hostno, int target, int lun);
extern int sysfs_for_each_device(int host_no, uint32_t sid,
				 void (* fn)(int host_no, int target, int lun));
extern struct iscsi_transport *get_transport_by_hba(long host_no);
extern struct iscsi_transport *get_transport_by_session(char *sys_session);
extern struct iscsi_transport *get_transport_by_sid(uint32_t sid);
extern struct iscsi_transport *get_transport_by_name(char *transport_name);
extern int free_transport_by_handle(uint64_t handle);

extern struct list_head transports;

#endif
