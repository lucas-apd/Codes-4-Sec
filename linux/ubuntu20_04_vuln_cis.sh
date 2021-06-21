#!/bin/bash

# Check Ubuntu 20.04 Workstation:
# https://www.open-scap.org/tools/openscap-base/
#sudo apt install ssg-base ssg-debderived ssg-debian ssg-nondebian ssg-applications libopenscap8 -y
# Check Ubuntu vulnerabilities:

# Option 1
wget https://security-metadata.canonical.com/oval/com.ubuntu.$(lsb_release -cs).usn.oval.xml.bz2
bunzip2 com.ubuntu.$(lsb_release -cs).usn.oval.xml.bz2
rm com.ubuntu.$(lsb_release -cs).usn.oval.xml.bz2
oscap oval eval --report vuln-report-$(hostname).html com.ubuntu.$(lsb_release -cs).usn.oval.xml
xdg-open vuln-report-$(hostname).html > /dev/null
 

# Check Ubuntu cis compliance:
# Option 1

wget https://github.com/ComplianceAsCode/content/releases/download/v0.1.56/scap-security-guide-0.1.56-oval-510.zip
unzip scap-security-guide-0.1.56-oval-510.zip
rm scap-security-guide-0.1.56-oval-510.zip
oscap oval eval --report cis-report-$(hostname).html scap-security-guide-0.1.56-oval-5.10/ssg-ubuntu2004-ds.xml
xdg-open cis-report-$(hostname).html > /dev/null
 
 
# Option 2 DISA
# https://nvd.nist.gov/ncp/checklist/992/download/6825
wget https://dl.dod.cyber.mil/wp-content/uploads/stigs/zip/U_CAN_Ubuntu_20-04_LTS_V1R1_STIG.zip
unzip U_CAN_Ubuntu_20-04_LTS_V1R1_STIG.zip
rm U_CAN_Ubuntu_20-04_LTS_V1R1_STIG.zip
oscap xccdf  eval --report disa-report-$(hostname).html U_CAN_Ubuntu_20-04_LTS_V1R1_Manual_STIG/U_CAN_Ubuntu_20-04_LTS_STIG_V1R1_Manual-xccdf.xml 


# Option 3 
sudo apt install -y ansible
sudo sh -c "echo '- src: https://github.com/florianutz/ubuntu2004_cis.git' >> /etc/ansible/requirements.yml"
cd /etc/ansible/
sudo ansible-galaxy install -p roles -r /etc/ansible/requirements.yml
sudo sh -c "cat > /etc/ansible/harden.yml <<EOF
- name: Harden Server
  hosts: localhost
  connection: local
  become: yes

  roles:
    - ubuntu2004_cis
    
EOF
"
sudo ansible-playbook /etc/ansible/harden.yml

# Quick Hardening

apt-get update
apt-get upgrade
apt-get autoremove
apt-get autoclean
apt-get install unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades
echo 'APT::Periodic::AutocleanInterval “7”;' &>> /etc/apt/apt.conf.d/20auto-upgrades

# Enable Firewall and set default config:
ufw --force enable
ufw default deny incoming
ufw default allow outgoing
ufw allow in on lo
ufw allow out on lo
ufw reload

# Block IP Spoofing:
echo ": order bind,hosts" &>> /etc/host.conf
echo ": nospoof on" &>> /etc/host.conf
echo net.ipv4.conf.all.rp_filter=1 &>> /etc/sysctl.conf
echo net.ipv4.conf.default.rp_filter=1 &>> /etc/sysctl.conf
/etc/rc.d/init.d/network restart

