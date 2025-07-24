# BinPool

<p align="center">
<img src="images/binpool-logo.png" alt="Project Logo" width="300"/>
</p>

## Table of Contents
- [Introduction](#introduction)
- [Access](#access)
- [Features](#features)
- [Structure](#structure)
- [Installation](#installation)
- [Automation](#automation)
- [Usage](#usage)
- [Statistics](#statistics)
- [Team](#team)

## Introduction

This repository hosts the paper *BinPool: A Dataset of Vulnerabilities for Binary Security Analysis*.  
BinPool is a dataset consisting of vulnerable and patched binaries derived from historical Debian packages, compiled using four different optimization levels. It can be used for vulnerability discovery tasks through various methods, including machine learning and static analysis. If you want to get familiar with BinPool please watch this video. 

🎥 **Learn more about BinPool by watching our introduction video:**  
[![Watch the video](https://img.youtube.com/vi/5Iry-2FybP0/0.jpg)](https://youtu.be/5Iry-2FybP0?si=8AwZuvgp1gRKVnd9)

## Access

You can download the dataset from [Zenodo](https://zenodo.org/records/15178740?token=eyJhbGciOiJIUzUxMiJ9.eyJpZCI6IjYyNjNiOWM1LTU0MDUtNGZhNi04Y2JiLTljNmU1YTFlYTY1ZSIsImRhdGEiOnt9LCJyYW5kb20iOiI0YmUwNTVkODZlNzljOWMxN2JhNzA1OTVjMzcyMWMzYyJ9.SweHr1Ywaw-sKt8WEe17cZvgg53iLDqlRsW7mVLewqEAoQD1ZqJxkiCyUYU073acwED5HbN_yg8Kj5GAl4h3Bg).

## Features
BinPool provides the following features:
BinPool provides the following features:
- Provides 603 unique CVEs and more than 80 CWEs.
- Includes the fix version of the corresponding Debian package for each CVE.
- Covers various programming languages (C, C++, Java, Python, PHP).
- Provides function and module names present in both patch and binary versions.

| **Measurement**                  | **Value** |
|----------------------------------|-----------|
| Number of Unique CVEs            | 603       |
| Number of CWEs                   | 89        |
| Number of Debian Files           | 824       |
| Total Number of Binaries         | 6144      |
| Number of Debian Packages        | 162       |
| Number of Source Modules         | 768       |
| Number of Source Functions       | 910       |
| Number of Binary Functions       | 7280      |

Below is a list of the most frequent CWEs in BinPool:

| **CWE**     | **CWE Name**                                      | **Count**  |
|------------|---------------------------------------------------|------------|
| CWE-787    | Out-of-bounds Write                                | 71         |
| CWE-476    | NULL Pointer Dereference                           | 61         |
| CWE-125    | Out-of-bounds Read                                 | 54         |
| CWE-190    | Integer Overflow or Wraparound                     | 34         |
| CWE-20     | Improper Input Validation                          | 28         |
| CWE-416    | Use After Free                                     | 27         |
| CWE-400    | Uncontrolled Resource Consumption                  | 20         |

## Structure

After downloading the data, the structure will be as follows:

```
CVE-ID/
│
├── vulnerable/                # Directory containing vulnerable versions
│   ├── opt0/                  # Optimization level 0 for vulnerable version
│   ├── opt1/                  # Optimization level 1 for vulnerable version
│   ├── opt2/                  # Optimization level 2 for vulnerable version
│   └── opt3/                  # Optimization level 3 for vulnerable version
│
└── patch/                     # Directory containing patched versions
    ├── opt0/                  # Optimization level 0 for patched version
    ├── opt1/                  # Optimization level 1 for patched version
    ├── opt2/                  # Optimization level 2 for patched version
    └── opt3/                  # Optimization level 3 for patched version
```

## Installation

In this section, we explain the process behind how the BinPool dataset was created.

The Debian Security Tracker provides up-to-date CVE information for Debian packages in JSON format: [https://security-tracker.debian.org/tracker/data/json](https://security-tracker.debian.org/tracker/data/json)  
Each CVE entry includes the package name and the version that fixes it. All this data is compiled [here](https://docs.google.com/spreadsheets/d/1qztIwB8xJ10H-2HLX15vI29Ze7yFDOrv7kDQ4JUi1g8/edit?usp=sharing). The full package list of Debian can be acceccable from https://docs.google.com/spreadsheets/d/1QKJ6mVC-G2qrCmaN2Z1MxKqO4598YOuyZPcuIywykik/edit?gid=477866570#gid=477866570

We download the package source for each CVE using the following steps:

1. Visit [Debian Snapshot](https://snapshot.debian.org/), select "Source Packages", and search for the package name (e.g., `tigervnc`). Select the required version and copy the `.dsc` source file link under the "Source Files" section. We also provide an automated script to help find this source link.

2. **Finding the correct Debian version for the environment setup is critical**. This is automated in our scripts. The correct Debian version ensures all package dependencies are properly installed.

3. You can manually set up the environment using a virtual machine or, preferably, using `debootstrap`:

```bash
sudo apt-get update
sudo apt-get install debootstrap
sudo mkdir /mnt/debian
```

Now install Debian 10 (buster) inside the created directory:

```bash
sudo debootstrap --arch amd64 buster /mnt/debian http://deb.debian.org/debian
sudo chroot /mnt/debian
```

4. You are now inside the Debian chroot. Install necessary dependencies:

```bash
apt-get update
apt-get install -y --force-yes build-essential fakeroot devscripts packaging-dev
```

5. Create and enter a directory for the vulnerable version:

```bash
mkdir vulnerable
cd vulnerable
```

6. Download the source using `dget`:

```bash
dget -u --insecure <source_file_url>
```

Example:

```bash
dget -u --insecure https://snapshot.debian.org/archive/debian-debug/20161230T030620Z/pool/main/t/tigervnc/tigervnc_1.7.0-2.dsc
```

Inside each Debian package, there is a `/debian/patches/` directory. It contains all applied patches. For example, in `tigervnc_1.10.1+dfsg-4`, you'll find:

<img src="images/tigervnc.png" width="1000"/>

The file `series` lists all patches. Use the tool `quilt` to manage patches:

```bash
quilt applied       # shows applied patches
quilt pop <patch>   # remove specific patch
quilt pop -a        # remove all patches
```

More on `quilt`: [https://raphaelhertzog.com/2012/08/08/how-to-use-quilt-to-manage-patches-in-debian-packages/](https://raphaelhertzog.com/2012/08/08/how-to-use-quilt-to-manage-patches-in-debian-packages/)

7. Build package dependencies:

```bash
apt build-dep .
```

8. Build the package with debug info and various optimization levels:

```bash
# Optimization level 0
yes '' | DEB_BUILD_OPTIONS='nostrip noopt debug' dpkg-buildpackage -b -uc -us

# Optimization level 1
export CFLAGS="-O1"
export CXXFLAGS="-O1"
export FFLAGS="-O1"
export DEB_BUILD_OPTIONS="nostrip debug"
dpkg-buildpackage -b -uc -us

# Optimization level 2
export CFLAGS="-O2"
export CXXFLAGS="-O2"
export FFLAGS="-O2"
export DEB_BUILD_OPTIONS="nostrip debug"
dpkg-buildpackage -b -uc -us

# Optimization level 3
export CFLAGS="-O3"
export CXXFLAGS="-O3"
export FFLAGS="-O3"
export DEB_BUILD_OPTIONS="nostrip debug"
dpkg-buildpackage -b -uc -us
```

For the patched version, apply all patches:

```bash
quilt push -a
```

Then rebuild the package with the same steps.

## Automation

All steps above are automated in [binpool_automation](https://github.com/GiorgosNikitopoulos/binpool_automation).

## Usage

After downloading the dataset, run `extract_deb_tar.py` to extract Debian files into binaries. The resulting structure should look like this:

```
CVE-ID/
│
├── vulnerable/                
│   ├── opt0/                  
│   │   └── debfiles/          
│   │       └── bins/          
│   ├── opt1/
│   │   └── debfiles/
│   │       └── bins/
│   ├── opt2/
│   │   └── debfiles/
│   │       └── bins/
│   └── opt3/
│       └── debfiles/
│           └── bins/
│
└── patch/
    ├── opt0/
    │   └── debfiles/
    │       └── bins/
    ├── opt1/
    │   └── debfiles/
    │       └── bins/
    ├── opt2/
    │   └── debfiles/
    │       └── bins/
    └── opt3/
        └── debfiles/
            └── bins/
```

## Statistics

All BinPool statistics are collected in the repository.

To extract the statistics, run:

```bash
python3 extract_statistics.py 
```
here is a link to binpool_info.json.[binpool_info.json](https://github.com/SimaArasteh/binpool/blob/main/binpool_info.json) 

## Team

**Sima Arasteh** – PhD Student, University of Southern California  
**Georgios Nikitopoulos** – PhD Student, Dartmouth College  
**Wei-Cheng Wu** – PhD Student, Dartmouth College  
**Nicolaas Weideman** – PhD Student, USC ISI  
**Aaron Portnoy** – Hacker-in-Residence, Dartmouth College  
**Mukund Raghothaman** – Assistant Professor, University of Southern California  
**Christophe Hauser** – Assistant Professor, Dartmouth College  
