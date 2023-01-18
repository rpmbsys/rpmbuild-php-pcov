# Fedora spec file for php-pecl-pcov
# with SCL stuff removed from:
#
# remirepo spec file for php-pecl-pcov
#
# Copyright (c) 2019-2021 Remi Collet
# License: CC-BY-SA
# http://creativecommons.org/licenses/by-sa/4.0/
#
# Please, preserve the changelog entries
#
%global with_zts  0%{!?_without_zts:%{?__ztsphp:1}}
%global pecl_name pcov
%global ini_name  40-%{pecl_name}.ini

%define _debugsource_template %{nil}
%define debug_package %{nil}

Summary:        Code coverage driver
Name:           php-pecl-%{pecl_name}
Version:        1.0.11
Release:        1%{?dist}
License:        PHP
URL:            https://pecl.php.net/package/%{pecl_name}
Source0:        https://pecl.php.net/get/%{pecl_name}-%{version}.tgz

BuildRequires:  make
BuildRequires:  gcc
BuildRequires:  php-devel >= 7.1
BuildRequires:  php-pear

Requires:       php(zend-abi) = %{php_zend_api}
Requires:       php(api) = %{php_core_api}

Provides:       php-%{pecl_name}               = %{version}
Provides:       php-%{pecl_name}%{?_isa}       = %{version}
Provides:       php-pecl(%{pecl_name})         = %{version}
Provides:       php-pecl(%{pecl_name})%{?_isa} = %{version}


%description
A self contained php-code-coverage compatible driver for PHP7.


%prep
%setup -q -c
mv %{pecl_name}-%{version} NTS

# Don't install/register tests
sed -e 's/role="test"/role="src"/' \
    -e '/LICENSE/s/role="doc"/role="src"/' \
    -i package.xml

cd NTS

# Sanity check, really often broken
extver=$(sed -n '/#define PHP_PCOV_VERSION/{s/.* "//;s/".*$//;p}' php_pcov.h)
if test "x${extver}" != "x%{version}%{?prever:-%{prever}}"; then
   : Error: Upstream extension version is ${extver}, expecting %{version}%{?prever:-%{prever}}.
   exit 1
fi
cd ..

%if %{with_zts}
# Duplicate source tree for NTS / ZTS build
cp -pr NTS ZTS
%endif

# Create configuration file
cat << 'EOF' | tee %{ini_name}
; Enable %{pecl_name} extension module
extension=%{pecl_name}.so

; Configuration

; The recommended defaults for production should be:
pcov.enabled = 0

; The recommended defaults for development should be:
;pcov.enabled = 1
;pcov.directory = /path/to/your/source/directory
;pcov.exclude = ''
;pcov.initial.memory = 65536
;pcov.initial.files = 64
EOF


%build
cd NTS
%{_bindir}/phpize
%configure \
    --enable-pcov \
    --with-libdir=%{_lib} \
    --with-php-config=%{_bindir}/php-config

make %{?_smp_mflags}

%if %{with_zts}
cd ../ZTS
%{_bindir}/zts-phpize
%configure \
    --enable-pcov \
    --with-libdir=%{_lib} \
    --with-php-config=%{_bindir}/zts-php-config

make %{?_smp_mflags}
%endif


%install
make -C NTS install INSTALL_ROOT=%{buildroot}

# install config file
install -D -m 644 %{ini_name} %{buildroot}%{php_inidir}/%{ini_name}

# Install XML package description
install -D -m 644 package.xml %{buildroot}%{pecl_xmldir}/%{name}.xml

%if %{with_zts}
make -C ZTS install INSTALL_ROOT=%{buildroot}

install -D -m 644 %{ini_name} %{buildroot}%{php_ztsinidir}/%{ini_name}
%endif

# Documentation
cd NTS
for i in $(grep 'role="doc"' ../package.xml | sed -e 's/^.*name="//;s/".*$//')
do install -Dpm 644 $i %{buildroot}%{pecl_docdir}/%{pecl_name}/$i
done


%check
: Minimal load test for NTS extension
cd NTS
%{_bindir}/php --no-php-ini \
    --define extension=modules/%{pecl_name}.so \
    --modules | grep '^%{pecl_name}$'

: Upstream test suite for NTS extension
TEST_PHP_EXECUTABLE=%{_bindir}/php \
TEST_PHP_ARGS="-n -d extension=$PWD/modules/%{pecl_name}.so" \
NO_INTERACTION=1 \
REPORT_EXIT_STATUS=1 \
%{_bindir}/php -n run-tests.php --show-diff


%if %{with_zts}
: Minimal load test for ZTS extension
cd ../ZTS
%{__ztsphp} --no-php-ini \
    --define extension=modules/%{pecl_name}.so \
    --modules | grep '^%{pecl_name}$'

: Upstream test suite for ZTS extension
TEST_PHP_EXECUTABLE=%{__ztsphp} \
TEST_PHP_ARGS="-n -d extension=$PWD/modules/%{pecl_name}.so" \
NO_INTERACTION=1 \
REPORT_EXIT_STATUS=1 \
%{__ztsphp} -n run-tests.php --show-diff
%endif


%files
%license NTS/LICENSE
%doc %{pecl_docdir}/%{pecl_name}
%{pecl_xmldir}/%{name}.xml

%config(noreplace) %{php_inidir}/%{ini_name}
%{php_extdir}/%{pecl_name}.so

%if %{with_zts}
%config(noreplace) %{php_ztsinidir}/%{ini_name}
%{php_ztsextdir}/%{pecl_name}.so
%endif


%changelog
* Tue Dec 21 2021 Remi Collet <remi@remirepo.net> - 1.0.11-1
- update to 1.0.11

* Wed Nov 24 2021 Remi Collet <remi@remirepo.net> - 1.0.10-1
- update to 1.0.10

* Fri Mar 19 2021 Remi Collet <remi@remirepo.net> - 1.0.7-1
- update to 1.0.7

* Thu Jan 30 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.0.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Thu Oct 03 2019 Remi Collet <remi@remirepo.net> - 1.0.6-1
- update to 1.0.6
- rebuild for https://fedoraproject.org/wiki/Changes/php74

* Fri Jul 26 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.0.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Tue Jun 11 2019 Remi Collet <remi@remirepo.net> - 1.0.5-1
- update to 1.0.5

* Mon Jun  3 2019 Remi Collet <remi@remirepo.net> - 1.0.4-1
- update to 1.0.4

* Mon May  6 2019 Remi Collet <remi@remirepo.net> - 1.0.3-1
- update to 1.0.3

* Sun Mar 31 2019 Remi Collet <remi@remirepo.net> - 1.0.2-1
- update to 1.0.2

* Mon Mar 25 2019 Remi Collet <remi@remirepo.net> - 1.0.1-1
- update to 1.0.1

* Fri Feb  1 2019 Remi Collet <remi@remirepo.net> - 1.0.0-2
- cleanup SCL stuff for Fedora review

* Wed Jan 30 2019 Remi Collet <remi@remirepo.net> - 1.0.0-1
- update to 1.0.0 (stable)
- raise dependency on PHP 7.1
- switch to production recommended configuration

* Tue Jan 22 2019 Remi Collet <remi@remirepo.net> - 0.9.0-1
- initial package, version 0.9.0 (beta)
