#
# spec file for package open-iscsi
#
# Copyright (c) 2011 SUSE LINUX Products GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#

# norootforbuild


Name:           open-iscsi
BuildRequires:  autoconf bison db-devel flex
Url:            http://www.open-iscsi.org
License:        GPL v2 or later
Group:          Productivity/Networking/Other
PreReq:         %fillup_prereq %insserv_prereq
AutoReqProv:    on
Version:        2.0.872
Release:        0.<RELEASE26>
Provides:       linux-iscsi
Obsoletes:      linux-iscsi
%define iscsi_release 872
Summary:        Linux* Open-iSCSI Software Initiator
Source:         %{name}-2.0-%{iscsi_release}.tar.bz2
Source11:       iscsi-gen-initiatorname.sh
Patch1:         %{name}-git-update.diff.bz2
Patch2:         %{name}-git-merge.diff.bz2
Patch3:         %{name}-brcm_iscsi_uio.diff.bz2
Patch4:         %{name}-sles11-sp2.diff.bz2
BuildRoot:      %{_tmppath}/%{name}-%{version}-build

%description
Open-iSCSI is a high-performance, transport independent, multi-platform
implementation of RFC3720 iSCSI.

Open-iSCSI is partitioned into user and kernel parts.

The kernel portion of Open-iSCSI is a from-scratch code licensed under
GPL. The kernel part implements iSCSI data path (that is, iSCSI Read
and iSCSI Write), and consists of two loadable modules: iscsi_if.ko and
iscsi_tcp.ko.

User space contains the entire control plane: configuration manager,
iSCSI Discovery, Login and Logout processing, connection-level error
processing, Nop-In and Nop-Out handling, and (in the future:) Text
processing, iSNS, SLP, Radius, etc.

The user space Open-iSCSI consists of a daemon process called iscsid,
and a management utility iscsiadm.



Authors:
--------
    open-iscsi@googlegroups.com

%prep
%setup -n %{name}-2.0-%{iscsi_release}
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1

%build
%{__make} OPTFLAGS="${RPM_OPT_FLAGS} -DLOCK_DIR=\\\"/etc/iscsi\\\"" user
cd brcm_iscsi_uio
touch NEWS
touch AUTHORS
autoreconf --install
%configure --sbindir=/sbin
make CFLAGS="${RPM_OPT_FLAGS}"

%install
make DESTDIR=${RPM_BUILD_ROOT} install_user
make DESTDIR=${RPM_BUILD_ROOT} install_initd_suse
(cd brcm_iscsi_uio; make DESTDIR=${RPM_BUILD_ROOT} install)
install -D -m 755 %{S:11} ${RPM_BUILD_ROOT}/sbin/iscsi-gen-initiatorname
(cd ${RPM_BUILD_ROOT}/sbin; ln -sf /etc/init.d/open-iscsi rcopen-iscsi)
(cd ${RPM_BUILD_ROOT}/etc; ln -sf iscsi/iscsid.conf iscsid.conf)

%clean
[ "${RPM_BUILD_ROOT}" != "/" -a -d ${RPM_BUILD_ROOT} ] && rm -rf ${RPM_BUILD_ROOT}

%post
[ -x /sbin/mkinitrd_setup ] && mkinitrd_setup
%{fillup_and_insserv -Y boot.open-iscsi}
if [ ! -f /etc/iscsi/initiatorname.iscsi ] ; then
    /sbin/iscsi-gen-initiatorname
fi

%postun
[ -x /sbin/mkinitrd_setup ] && mkinitrd_setup
%{insserv_cleanup}

%preun
%{stop_on_removal open-iscsi}

%files
%defattr(-,root,root)
%dir /etc/iscsi
%attr(0600,root,root) %config(noreplace) /etc/iscsi/iscsid.conf
%attr(0600,root,root) %config(noreplace) /etc/iscsi/initiatorname.iscsi
%dir /etc/iscsi/ifaces
%config /etc/iscsi/ifaces/iface.example
/etc/iscsid.conf
%config /etc/init.d/open-iscsi
%config /etc/init.d/boot.open-iscsi
/sbin/*
/etc/logrotate.d/*
%dir /lib/mkinitrd
%dir /lib/mkinitrd/scripts
/lib/mkinitrd/scripts/setup-iscsi.sh
/lib/mkinitrd/scripts/boot-iscsi.sh
/lib/mkinitrd/scripts/boot-killiscsi.sh
%doc COPYING README
%doc %{_mandir}/man8/*

%changelog