#!/bin/bash

# Check Ubuntu Workstation vulnerabilities:

# Check Ubuntu vulnerabilities:

# Option 1
wget https://security-metadata.canonical.com/oval/com.ubuntu.$(lsb_release -cs).usn.oval.xml.bz2
bunzip2 com.ubuntu.$(lsb_release -cs).usn.oval.xml.bz2
sudo rm com.ubuntu.$(lsb_release -cs).usn.oval.xml.bz2
oscap oval eval --report vuln-report-$(hostname).html com.ubuntu.$(lsb_release -cs).usn.oval.xml
xdg-open vuln-report-$(hostname).html > /dev/null


# Check Ubuntu cis compliance:

# Option 1
sudo wget https://github.com/ComplianceAsCode/content/releases/download/v0.1.56/scap-security-guide-0.1.56-oval-510.zip
sudo unzip scap-security-guide-0.1.56-oval-510.zip
sudo rm scap-security-guide-0.1.56-oval-510.zip
oscap oval eval --report cis-report-$(hostname).html scap-security-guide-0.1.56-oval-5.10/ssg-ubuntu2004-ds-1.2.xml
xdg-open cis-report-$(hostname).html > /dev/null

# Option 2
sudo apt install -y libopenscap8 xsltproc unzip ansible
sudo sh -c "echo '- src: https://github.com/florianutz/Ubuntu1804-CIS.git' >> requirements.yml"
sudo ansible-galaxy install -p roles -r requirements.yml
sudo sh -c "cat > harden.yml <<EOF
- name: Harden Server
  hosts: localhost
  connection: local
  become: yes

  roles:
    - ubuntu2004_cis
    
EOF
"
sudo ansible-playbook harden.yml
