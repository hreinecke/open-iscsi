#
# spec file for package open-iscsi
#
# Copyright (c) 2014 SUSE LINUX Products GmbH, Nuernberg, Germany.
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


Name:           open-iscsi
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  bison
BuildRequires:  db-devel
BuildRequires:  flex
BuildRequires:  libtool
BuildRequires:  make
BuildRequires:  openssl-devel
%if 0%{?suse_version} >= 1230
BuildRequires:  systemd
%endif
Url:            http://www.open-iscsi.org
PreReq:         %fillup_prereq %insserv_prereq
Version:        2.0.873
Release:        0
%{?systemd_requires}
Recommends:     logrotate
%define iscsi_release 873
Summary:        Linux* Open-iSCSI Software Initiator
License:        GPL-2.0+
Group:          Productivity/Networking/Other
Source:         %{name}-2.0-%{iscsi_release}.tar.bz2
Source1:        %{name}-firewall.service
Patch1:         %{name}-Factory-latest.diff.bz2
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

%package -n open-isns
Summary:        Linux iSNS server
Group:          Productivity/Networking/Other
Version:        0.90
Release:        0
Obsoletes:      isns <= 2.1.02
Provides:       isns = 2.1.03

%description -n open-isns
This is a partial implementation of iSNS, according to RFC4171.
The implementation is still somewhat incomplete, but I am releasing
it for your reading pleasure.

Authors:
--------
    Olaf Kirch <okir@suse.de>

%package -n iscsiuio
Summary:        Linux Broadcom NetXtremem II iscsi server
Group:          Productivity/Networking/Other
Version:        0.7.8.2
Release:        0

%description -n iscsiuio
This tool is to be used in conjunction with the Broadcom NetXtreme II Linux
driver (Kernel module name: 'bnx2' and 'bnx2x'), Broadcom CNIC driver,
and the Broadcom iSCSI driver (Kernel module name: 'bnx2i').
This user space tool is used in conjunction with the following
Broadcom Network Controllers:
  bnx2:  BCM5706, BCM5708, BCM5709 devices
  bnx2x: BCM57710, BCM57711, BCM57711E, BCM57712, BCM57712E,
         BCM57800, BCM57810, BCM57840 devices

This utility will provide the ARP and DHCP functionality for the iSCSI offload.
The communication to the driver is done via Userspace I/O (Kernel module name
'uio').

Authors:
--------
    Eddie Wai <eddie.wai@broadcom.com>
    Benjamin Li <benli@broadcom.com>

%prep
%setup -n %{name}-2.0-%{iscsi_release}
%patch1 -p1

%build
%{__make} OPTFLAGS="${RPM_OPT_FLAGS} -fno-strict-aliasing -DOFFLOAD_BOOT_SUPPORTED -DLOCK_DIR=\\\"/etc/iscsi\\\"" LDFLAGS="" user
%{__make} OPTFLAGS="${RPM_OPT_FLAGS}" -C utils/open-isns programs
cd iscsiuio
touch NEWS
touch AUTHORS
autoreconf --install
%configure --sbindir=/sbin
make CFLAGS="${RPM_OPT_FLAGS}"

%install
make DESTDIR=${RPM_BUILD_ROOT} install_user
make DESTDIR=${RPM_BUILD_ROOT} install_mkinitrd_suse
# install service files
%if 0%{?suse_version} >= 1230
make DESTDIR=${RPM_BUILD_ROOT} install_service_suse
%else
make DESTDIR=${RPM_BUILD_ROOT} install_initd_suse
# rename open-iscsi service to iscsid for openSUSE
mv ${RPM_BUILD_ROOT}/etc/init.d/boot.open-iscsi \
	${RPM_BUILD_ROOT}/etc/init.d/boot.iscsid-early
mv ${RPM_BUILD_ROOT}/etc/init.d/open-iscsi \
	${RPM_BUILD_ROOT}/etc/init.d/iscsid
# create rc shortcut
[ -d ${RPM_BUILD_ROOT}/usr/sbin ] || mkdir -p ${RPM_BUILD_ROOT}/usr/sbin
ln -sf ../../etc/init.d/iscsid ${RPM_BUILD_ROOT}/usr/sbin/rciscsid
%endif
(cd ${RPM_BUILD_ROOT}/etc; ln -sf iscsi/iscsid.conf iscsid.conf)
touch ${RPM_BUILD_ROOT}/etc/iscsi/initiatorname.iscsi
install -m 0755 usr/iscsistart %{buildroot}/sbin
make DESTDIR=${RPM_BUILD_ROOT} -C utils/open-isns install
%if 0%{?suse_version} >= 1230
make DESTDIR=${RPM_BUILD_ROOT} -C utils/open-isns install_service
%endif
make DESTDIR=${RPM_BUILD_ROOT} -C iscsiuio install
# install firewall file for isns server
install -vD %{S:1} %{buildroot}/etc/sysconfig/SuSEfirewall2.d/services/isns

%clean
[ "${RPM_BUILD_ROOT}" != "/" -a -d ${RPM_BUILD_ROOT} ] && rm -rf ${RPM_BUILD_ROOT}

%post
[ -x /sbin/mkinitrd_setup ] && mkinitrd_setup
if [ ! -f /etc/iscsi/initiatorname.iscsi ] ; then
    /sbin/iscsi-gen-initiatorname
fi
%if 0%{?suse_version} >= 1230
%{service_add_post iscsid.socket iscsid.service iscsi.service}
%else
%{fillup_and_insserv -Y boot.iscsid-early}
%endif

%postun
[ -x /sbin/mkinitrd_setup ] && mkinitrd_setup
%if 0%{?suse_version} >= 1230
%{service_del_postun iscsid.socket iscsid.service iscsi.service}
%else
%{insserv_cleanup}
%endif

%pre
%if 0%{?suse_version} >= 1230
%{service_add_pre iscsid.socket iscsid.service iscsi.service}
%endif

%preun
%{stop_on_removal iscsid}
%if 0%{?suse_version} >= 1230
%{service_del_preun iscsid.socket iscsid.service iscsi.service}
%endif

%post -n open-isns
%if 0%{?suse_version} >= 1230
%{service_add_post isnsd.socket isnsd.service}
%endif

%postun -n open-isns
%if 0%{?suse_version} >= 1230
%{service_add_post isnsd.socket isnsd.service}
%endif

%pre -n open-isns
%if 0%{?suse_version} >= 1230
%{service_add_pre isnsd.socket isnsd.service}
%endif

%preun -n open-isns
%{stop_on_removal isnsd isnsdd}
%if 0%{?suse_version} >= 1230
%{service_del_preun isnsd.socket isnsd.service}
%endif

%post -n iscsiuio
%if 0%{?suse_version} >= 1230
%{service_add_post iscsiuio.socket iscsiuio.service}
%endif

%postun -n iscsiuio
%if 0%{?suse_version} >= 1230
%{service_add_post iscsiuio.socket iscsiuio.service}
%endif

%pre -n iscsiuio
%if 0%{?suse_version} >= 1230
%{service_add_pre iscsiuio.socket iscsiuio.service}
%endif

%preun -n iscsiuio
%{stop_on_removal iscsiuio}
%if 0%{?suse_version} >= 1230
%{service_del_preun iscsiuio.socket iscsiuio.service}
%endif

%files
%defattr(-,root,root)
%dir /etc/iscsi
%attr(0600,root,root) %config(noreplace) /etc/iscsi/iscsid.conf
%ghost /etc/iscsi/initiatorname.iscsi
%dir /etc/iscsi/ifaces
%config /etc/iscsi/ifaces/iface.example
/etc/iscsid.conf
%if 0%{?suse_version} >= 1230
%{_unitdir}/iscsid.service
%{_unitdir}/iscsid.socket
%{_unitdir}/iscsi.service
/usr/lib/systemd/system-generators/ibft-rule-generator
%else
%config /etc/init.d/iscsid
%config /etc/init.d/boot.iscsid-early
/usr/sbin/rciscsid
%endif
/sbin/iscsid
/sbin/iscsiadm
/sbin/iscsi-iname
/sbin/iscsistart
/sbin/iscsi-gen-initiatorname
/sbin/iscsi_offload
/sbin/iscsi_discovery
%dir /lib/mkinitrd
%dir /lib/mkinitrd/scripts
/lib/mkinitrd/scripts/setup-iscsi.sh
/lib/mkinitrd/scripts/boot-iscsi.sh
/lib/mkinitrd/scripts/boot-killiscsi.sh
%doc COPYING README
%doc %{_mandir}/man8/iscsiadm.8.gz
%doc %{_mandir}/man8/iscsid.8.gz
%doc %{_mandir}/man8/iscsi_discovery.8.gz
%doc %{_mandir}/man8/iscsistart.8.gz
%doc %{_mandir}/man8/iscsi-iname.8.gz

%files -n open-isns
%defattr(-,root,root)
%dir /etc/isns
%attr(0600,root,root) %config(noreplace) /etc/isns/isnsd.conf
%attr(0600,root,root) %config(noreplace) /etc/isns/isnsdd.conf
%attr(0644,root,root) %config /etc/sysconfig/SuSEfirewall2.d/services/isns
%if 0%{?suse_version} >= 1230
%{_unitdir}/isnsd.service
%{_unitdir}/isnsd.socket
%endif
/usr/sbin/isnsd
/usr/sbin/isnsdd
/usr/sbin/isnsadm
%doc %{_mandir}/man8/isnsadm.8.gz
%doc %{_mandir}/man8/isnsd.8.gz
%doc %{_mandir}/man8/isnsdd.8.gz
%doc %{_mandir}/man5/isns_config.5.gz

%files -n iscsiuio
%defattr(-,root,root)
/sbin/iscsiuio
/sbin/brcm_iscsiuio
%doc %{_mandir}/man8/iscsiuio.8.gz
%config /etc/logrotate.d/iscsiuiolog
%if 0%{?suse_version} >= 1230
%{_unitdir}/iscsiuio.service
%{_unitdir}/iscsiuio.socket
%endif

%changelog
