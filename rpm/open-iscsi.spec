#
# spec file for package open-iscsi
#
# Copyright (c) 2017 SUSE LINUX GmbH, Nuernberg, Germany.
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
BuildRequires:  libmount-devel
BuildRequires:  libtool
BuildRequires:  make
BuildRequires:  openssl-devel
BuildRequires:  systemd
Url:            http://www.open-iscsi.org
PreReq:         %fillup_prereq %insserv_prereq
Version:        2.0.873
Release:        0
%{?systemd_requires}
%define iscsi_release 873
Summary:        Linux* Open-iSCSI Software Initiator
License:        GPL-2.0+
Group:          Productivity/Networking/Other
Source:         %{name}-2.0-%{iscsi_release}.tar.bz2
Patch1:         %{name}-git-update.diff.bz2
Patch2:         %{name}-sles12-update.diff.bz2
%define isns_name open-isns
%define isns_ver 0.95
Source10:       %{isns_name}-v%{isns_ver}.tar.bz2
Source11:       %{name}-firewall.service
Patch11:        %{isns_name}-Install-isns_config.5.patch
Patch12:        %{isns_name}-Update-GPL-license-information.patch
Patch13:        %{isns_name}-Fix-DD-member-doubling-when-restoring-from-DB.patch
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

%package -n iscsiuio
Summary:        Linux Broadcom NetXtremem II iscsi server
License:        GPL-2.0+
Group:          Productivity/Networking/Other
Version:        0.7.8.2
Release:        0
Requires:       logrotate

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

%package -n open-isns
Summary:        Partial Implementation of iSNS iSCSI registration
License:        LGPL-2.1+
Group:          System Environment/Kernel
Version:        0.95
Release:        0
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  glibc-devel
BuildRequires:  make
BuildRequires:  openssl-devel
BuildRequires:  systemd-rpm-macros
%{?systemd_requires}
Requires:       coreutils

%description -n open-isns
This is a partial implementation of the iSNS protocol (see below),
which supplies directory services for iSCSI initiators and targets.

The iSNS protocol is specified in
[RFC 4171](http://tools.ietf.org/html/rfc4171) and its purpose is to
make easier to discover, manage, and configure iSCSI devices. With
iSNS, iSCSI targets can be registered to a central iSNS server and
initiators can be configured to discover the targets by asking the
iSNS server.

%prep
%setup -n %{name}-2.0-%{iscsi_release}
%patch1 -p1
%patch2 -p1
%setup -n %{name}-2.0-%{iscsi_release} -T -D -a 10
%patch11 -p1
%patch12 -p1
%patch13 -p1

%build
cd %{isns_name}-%{isns_ver}
autoconf
autoheader
%configure --prefix=%{_prefix}
%{__make} OPTFLAGS="${RPM_OPT_FLAGS} -I include"
cd ..
%{__make} OPTFLAGS="${RPM_OPT_FLAGS} -fno-strict-aliasing -DOFFLOAD_BOOT_SUPPORTED -DLOCK_DIR=\\\"/etc/iscsi\\\" -I %{_builddir}/%{buildsubdir}/%{isns_name}-%{isns_ver}/include" LDFLAGS="-L%{_builddir}/%{buildsubdir}/%{isns_name}-%{isns_ver}" user
cd iscsiuio
touch NEWS
touch AUTHORS
autoreconf --install
%configure --sbindir=/sbin
%{__make} CFLAGS="${RPM_OPT_FLAGS}"

%install
make DESTDIR=${RPM_BUILD_ROOT} install_user
# install service files
make DESTDIR=${RPM_BUILD_ROOT} install_initd_suse
# create rc symlinks
[ -d ${RPM_BUILD_ROOT}/usr/sbin ] || mkdir -p ${RPM_BUILD_ROOT}/usr/sbin
ln -s %{_sbindir}/service %{buildroot}%{_sbindir}/rciscsi
ln -s %{_sbindir}/service %{buildroot}%{_sbindir}/rciscsid
ln -s %{_sbindir}/service %{buildroot}%{_sbindir}/rciscsiuio
(cd ${RPM_BUILD_ROOT}/etc; ln -sf iscsi/iscsid.conf iscsid.conf)
touch ${RPM_BUILD_ROOT}/etc/iscsi/initiatorname.iscsi
install -m 0755 usr/iscsistart %{buildroot}/sbin
make DESTDIR=${RPM_BUILD_ROOT} -C iscsiuio install
# install open-isns
cd %{isns_name}-%{isns_ver}
%{__make} DESTDIR=${RPM_BUILD_ROOT} install
if [ ! -d ${RPM_BUILD_ROOT}/usr/sbin ] ; then
        mkdir -p ${RPM_BUILD_ROOT}/usr/sbin
fi
ln -sf /usr/sbin/service ${RPM_BUILD_ROOT}/usr/sbin/rcisnsd
install -vD %{S:11} %{buildroot}/etc/sysconfig/SuSEfirewall2.d/services/isns

%clean
[ "${RPM_BUILD_ROOT}" != "/" -a -d ${RPM_BUILD_ROOT} ] && rm -rf ${RPM_BUILD_ROOT}

%post
if [ ! -f /etc/iscsi/initiatorname.iscsi ] ; then
    /sbin/iscsi-gen-initiatorname
fi
%{service_add_post iscsid.socket iscsid.service iscsi.service}

%postun
%{service_del_postun iscsid.socket iscsid.service iscsi.service}

%pre
%{service_add_pre iscsid.socket iscsid.service iscsi.service}

%preun
%{stop_on_removal iscsid}
%{service_del_preun iscsid.socket iscsid.service iscsi.service}

%post -n open-isns
%{service_add_post isnsd.socket isnsd.service}
# set up config files for this system
for f in /etc/isns/isnsadm.conf /etc/isns/isnsdd.conf; do
    sed -i -e 's/^#*\(ServerAddress[[:space:]]*=\).*/\1 localhost/' $f
done

%postun -n open-isns
%{service_del_postun isnsd.socket isnsd.service}

%pre -n open-isns
%{service_add_pre isnsd.socket isnsd.service}

%preun -n open-isns
%{stop_on_removal isnsd isnsdd}
%{service_del_preun isnsd.socket isnsd.service}

%post -n iscsiuio
%{service_add_post iscsiuio.socket iscsiuio.service}

%postun -n iscsiuio
%{service_del_postun iscsiuio.socket iscsiuio.service}

%pre -n iscsiuio
%{service_add_pre iscsiuio.socket iscsiuio.service}

%preun -n iscsiuio
%{stop_on_removal iscsiuio}
%{service_del_preun iscsiuio.socket iscsiuio.service}

%files
%defattr(-,root,root)
%dir /etc/iscsi
%attr(0600,root,root) %config(noreplace) /etc/iscsi/iscsid.conf
%ghost /etc/iscsi/initiatorname.iscsi
%dir /etc/iscsi/ifaces
%config /etc/iscsi/ifaces/iface.example
/etc/iscsid.conf
%{_unitdir}/iscsid.service
%{_unitdir}/iscsid.socket
%{_unitdir}/iscsi.service
/usr/lib/systemd/system-generators/ibft-rule-generator
%{_sbindir}/rciscsi
%{_sbindir}/rciscsid
/sbin/iscsid
/sbin/iscsiadm
/sbin/iscsi-iname
/sbin/iscsistart
/sbin/iscsi-gen-initiatorname
/sbin/iscsi_offload
/sbin/iscsi_discovery
/sbin/iscsi_fw_login
%doc COPYING README
%doc %{_mandir}/man8/iscsiadm.8.gz
%doc %{_mandir}/man8/iscsid.8.gz
%doc %{_mandir}/man8/iscsi_discovery.8.gz
%doc %{_mandir}/man8/iscsistart.8.gz
%doc %{_mandir}/man8/iscsi-iname.8.gz
%doc %{_mandir}/man8/iscsi_fw_login.8.gz
%dir /usr/lib/udev
%dir /usr/lib/udev/rules.d
/usr/lib/udev/rules.d/50-iscsi-firmware-login.rules

%files -n open-isns
%defattr(-,root,root)
%dir /etc/isns
%attr(0600,root,root) %config(noreplace) /etc/isns/isnsd.conf
%attr(0600,root,root) %config(noreplace) /etc/isns/isnsdd.conf
%attr(0600,root,root) %config(noreplace) /etc/isns/isnsadm.conf
%attr(0644,root,root) %config /etc/sysconfig/SuSEfirewall2.d/services/isns
%{_unitdir}/isnsd.service
%{_unitdir}/isnsd.socket
%{_sbindir}/rcisnsd
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
%{_unitdir}/iscsiuio.service
%{_unitdir}/iscsiuio.socket
%{_sbindir}/rciscsiuio

%changelog
