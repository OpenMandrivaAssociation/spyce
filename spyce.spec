%define name spyce
%define version 1.3.13
%define release %mkrel 1

%define httpd_conf /etc/httpd/conf/httpd.conf
%define httpd_conf_beginline ### BEGIN SPYCE CONFIG MARKER
%define httpd_conf_endline ### END SPYCE CONFIG MARKER
%define html_dir /var/www/html

Summary:       SPYCE - Python Server Pages, Python-based HTML scripting engine
Name:          %{name}
Version:       %{version}
Release:       %{release}
Group:         System/Servers
URL:           http://spyce.sourceforge.net
License:       Distributable 
BuildArch:     noarch
BuildRoot:     %{_builddir}/%{name}-builroot
BuildRequires: python >= 2.2
Requires:      python >= 2.2 , apache2
Source0:       %{name}-%{version}-1.tar.bz2

%description
SPYCE is a server-side engine that supports simple and efficient Python-based
dynamic HTML generation. Those who like Python and are familiar with JSP, or
PHP, or ASP, should have a look at this engine. It allows one to generate
dynamic HTML content just as easily, using Python for the dynamic parts. Its
modular design makes it very flexible and extensible. It can also be used as a
command-line utility for HTML pre-processing.

%prep

%setup -q

%build

make all

%install
rm -rf ${RPM_BUILD_ROOT}

make DESTDIR=${RPM_BUILD_ROOT} install

# to avoid creating files during post & postun
mkdir -p $RPM_BUILD_ROOT%_bindir
ln -sf %_datadir/%name/run_spyceCmd.py $RPM_BUILD_ROOT%_bindir/spyce


%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%_bindir/*
%_datadir/%name
%defattr(0644,root,root,755)
%doc docs/*

%post
echo -n "Generating Spyce parser tables..."
pushd /usr/share/spyce; /usr/bin/env python spyceParser.py; popd
#ln -sf /usr/share/spyce/run_spyceCmd.py /usr/bin/spyce

# FIXME : kept but to be replaced in install
ln -sf /usr/share/spyce/docs /usr/share/doc/spyce

echo -n "Adding Spyce config to httpd.conf..."
cp %httpd_conf %httpd_conf.spyce-install.bak
sed -e "/%httpd_conf_beginline/,/%httpd_conf_endline/d" \
  < %httpd_conf.spyce-install.bak > %httpd_conf
echo "%httpd_conf_beginline"                                 >> %httpd_conf
cat /usr/share/spyce/spyceApache.conf | sed -e "s+XXX+/usr/share/spyce+g"                             >> %httpd_conf
echo "%httpd_conf_endline"                                   >> %httpd_conf
echo " done."
/usr/sbin/apachectl graceful

%postun
if [ $1 == 0 ]; then 
#  rm -f /usr/share/doc/spyce
  rm -f %html_dir/spyce
  echo -n "Removing Spyce config from httpd.conf..."
  cp %httpd_conf %httpd_conf.spyce-uninstall.bak
  sed -e "/%httpd_conf_beginline/,/%httpd_conf_endline/d" \
    < %httpd_conf.spyce-uninstall.bak > %httpd_conf
  echo " done."
  /usr/sbin/apachectl graceful
fi

