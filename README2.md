# UMIS: The Units of Measurement Interporability Service 🚀

[![License: MIT](https://shields.io)](https://opensource.org)
[![Build Status](https://shields.io)](#)

## 📌 Overview
The FAIR representation of research data requires appropriate annotation of measured values with the correct unit. This 
project is a Dockerized version of the Units of Measurement Interoperability Service (UMIS), a web tool built to document
and align the digital representation of units of measurement to enable:
- interoperability of unit representations
- disambiguation of a unit from its string (in many formats)
- aggregation of all valid unit representation strings for a particular unit (with defining system)
- crosswalking of units from one format to another

## Features
1. Global search of unit strings
2. Identification of and information for:
   1. current unit representation systems
   2. quantitykinds
   3. systems of units
   4. systems of quantities
3. Unit crosswalk tool
4. Unit API

## ⚙️ Installation
This project is built using Django and PyMySQL.  The command line version uses sqlite as the database.
The Docker version of UMIS uses a MySQL image for the database.  The database behind UMIS as provided
via a separate (private) project so that its content can be managed. Therefore, updates can be either
i) an updated database file or ii) an updated version of the Django website.

Update to a supported version of Python. The, clone the repository and install the dependencies:

### Command Line
```bash
git clone https://github.com/usnistgov/nist_umis.git
cd nist_umis
pip install -r requirements.txt
python manage.py runserver
```

### Using Docker
TBA



## 🤝 Contributing
Contributions are always welcome! 
1. Fork this repository and contribute new features
2. Report issues in the issue tracker
3. Report new digital representation systems for units

## 📄 License
Distributed under the NIST License. See `License` for more information.
