#!/bin/bash
# Primeiro, instale versão mínima do Ubuntu 20.04:
# Salve o arquivo ubuntu20_04_vuln_cis.sh e execute: chmod +x ubuntu20_04_vuln_cis.sh
# Para executar os comandos abaixo use sudo: sudo ./ubuntu20_04_vuln_cis.sh

# Quick Hardening

# 1 - System configuration
apt-get update
apt-get upgrade
apt-get autoremove
apt-get autoclean
apt-get install unattended-upgrades
apt install syslog-ng -y
dpkg-reconfigure -plow unattended-upgrades
echo 'APT::Periodic::AutocleanInterval “7”;' &>> /etc/apt/apt.conf.d/20auto-upgrades

# 2 - Enable Firewall and set default config:
ufw --force enable
ufw default deny incoming
ufw default allow outgoing
ufw allow in on lo
ufw allow out on lo
ufw reload

# 3 - Blocking IP Spoofing:
echo ": order bind,hosts" &>> /etc/host.conf
echo ": nospoof on" &>> /etc/host.conf
echo net.ipv4.conf.all.rp_filter=1 &>> /etc/sysctl.conf
echo net.ipv4.conf.default.rp_filter=1 &>> /etc/sysctl.conf
/etc/rc.d/init.d/network restart

# 4 - USB guard install:
apt install --no-install-recommends usbguard
usbguard generate-policy > /tmp/rules.conf
install -m 0600 -o root -g root /tmp/rules.conf /etc/usbguard/rules.conf
systemctl enable usbguard.service
systemctl start usbguard.service

# 5 - Check Ubuntu vulnerabilities:

# https://www.open-scap.org/tools/openscap-base/
# sudo apt install ssg-base ssg-debderived ssg-debian ssg-nondebian ssg-applications libopenscap8 -y

# Option 1
wget https://security-metadata.canonical.com/oval/com.ubuntu.$(lsb_release -cs).usn.oval.xml.bz2
bunzip2 com.ubuntu.$(lsb_release -cs).usn.oval.xml.bz2
rm com.ubuntu.$(lsb_release -cs).usn.oval.xml.bz2
oscap oval eval --report vuln-report-$(hostname).html com.ubuntu.$(lsb_release -cs).usn.oval.xml
xdg-open vuln-report-$(hostname).html > /dev/null
 

# Check Ubuntu compliance report:
# Option 1

wget https://github.com/ComplianceAsCode/content/releases/download/v0.1.56/scap-security-guide-0.1.56-oval-510.zip
unzip scap-security-guide-0.1.56-oval-510.zip
rm scap-security-guide-0.1.56-oval-510.zip
oscap oval eval --report cis-report-$(hostname).html scap-security-guide-0.1.56-oval-5.10/ssg-ubuntu2004-ds.xml
xdg-open cis-report-$(hostname).html > /dev/null
 
 
# Option 2 DISA (todo)
# https://nvd.nist.gov/ncp/checklist/992/download/6825
#https://public.cyber.mil/stigs/downloads/?_dl_facet_stigs=operating-systems%2Cunix-linux
#https://nvd.nist.gov/feeds/xml/cpe/dictionary/official-cpe-dictionary_v2.3.xml.gz
wget https://dl.dod.cyber.mil/wp-content/uploads/stigs/zip/U_CAN_Ubuntu_20-04_LTS_V1R1_STIG.zip
unzip U_CAN_Ubuntu_20-04_LTS_V1R1_STIG.zip
rm U_CAN_Ubuntu_20-04_LTS_V1R1_STIG.zip
rm *.pdf
wget https://nvd.nist.gov/feeds/xml/cpe/dictionary/official-cpe-dictionary_v2.3.xml.gz
gzip -d official-cpe-dictionary_v2.3.xml.gz
oscap xccdf eval --report stig-report-$(hostname).html --profile MAC-2_Public --results results.xml --cpe official-cpe-dictionary_v2.3.xml U_CAN_Ubuntu_20-04_LTS_V1R1_Manual_STIG/U_CAN_Ubuntu_20-04_LTS_STIG_V1R1_Manual-xccdf.xml


