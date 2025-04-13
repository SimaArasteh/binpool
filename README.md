# BinPool

<p align="center">
<img src="images/binpool-logo.png" alt="Project Logo" width="300"/>
</p>

## Table of Contents
- [Introduction](#introduction)
- [Access](#Access)
- [Features](#features)
- [Structure](#Structure)
- [Installation](#installation)
- [Automation](#Automation)
- [Usage](#usage)
- [Statistics](#Statistics)
- [Team](#Team)

## Introduction

This is a repository of paper BinPool: A Dataset of Vulnerabilities for Binary Security Analysis.
BinPool is a dataset consisting of vulnerable and patched binaries derived from historical Debian packages compiled for four different optimization levels. BinPool can be used for vulnerability discovery tasks through various methods, including machine learning and static analysis. BinPool provides different features as follows. 

## Access
You can download the dataset from [https://zenodo.org/records/15178740?token=eyJhbGciOiJIUzUxMiJ9.eyJpZCI6IjYyNjNiOWM1LTU0MDUtNGZhNi04Y2JiLTljNmU1YTFlYTY1ZSIsImRhdGEiOnt9LCJyYW5kb20iOiI0YmUwNTVkODZlNzljOWMxN2JhNzA1OTVjMzcyMWMzYyJ9.SweHr1Ywaw-sKt8WEe17cZvgg53iLDqlRsW7mVLewqEAoQD1ZqJxkiCyUYU073acwED5HbN_yg8Kj5GAl4h3Bg](https://zenodo.org/records/15178740?token=eyJhbGciOiJIUzUxMiJ9.eyJpZCI6IjYyNjNiOWM1LTU0MDUtNGZhNi04Y2JiLTljNmU1YTFlYTY1ZSIsImRhdGEiOnt9LCJyYW5kb20iOiI0YmUwNTVkODZlNzljOWMxN2JhNzA1OTVjMzcyMWMzYyJ9.SweHr1Ywaw-sKt8WEe17cZvgg53iLDqlRsW7mVLewqEAoQD1ZqJxkiCyUYU073acwED5HbN_yg8Kj5GAl4h3Bg). 

## Features

- It Provides 603 number of unique CVEs and more than 80 CWEs.
- For each CVE, it provides the fix version of the debian package. 
- It covers different programming languages (C, C++, java, python, PHP)
- It provides function and module names exits in the patch and the binary contains the function.



| **Measurement**                  | **Value** |
|----------------------------------|-----------|
| Number of Unique CVEs            | 603       |
| Number of CWEs                   | 89        |
| Number of Debian files           | 824       |
| Total number of Binaries         | 6144      |
| Number of Debian Packages        | 162       |
| Number of source modules         | 768       |
| Number of source functions       | 910       |
| Number of Binary functions       | 7280      |


Below is a list of more frequent CWEs in Binpool.

| **CWE**     | **CWE-Name**                                      | **Number** |
|------------|---------------------------------------------------|------------|
| CWE-787    | Out-of-bounds Write                                | 71         |
| CWE-476    | NULL Pointer Dereference                           | 61         |
| CWE-125    | Out-of-bounds Read                                 | 54         |
| CWE-190    | CWE-190: Integer Overflow or Wraparound            | 34         |
| CWE-20     | Improper Input Validation                          | 28         |
| CWE-416    | Use After Free                                     | 27         |
| CWE-400    | Uncontrolled Resource Consumption                  | 20         |



## Structure

After downloading the data, you should see this structure.

```
CVE-ID/
│
├── vulnerable/                # Directory containing vulnerable versions
│   ├── opt0/                  # optimization level 0 for vulnerable version
│   ├── opt1/                  # optimization level 1 for vulnerable version
│   ├── opt2/                  # optimization level 2 for vulnerable version
│   └── opt3/                  # optimization level 3 for vulnerable version
│
└── patch/                     # Directory containing patched versions
    ├── opt0/                  # optimization level 0 for patched version
    ├── opt1/                  # optimization level 1 for patched version
    ├── opt2/                  # optimization level 2 for patched version
    └── opt3/                  # optimization level 3 for patched version

```


## Installation

In this Section, we explain the logic behind how we created the binpool dataset. 

Debian security tracker provides  the up to date CVEs in Debian packages in a json format.( https://security-tracker.debian.org/tracker/data/json ). For each CVE there is a package name and version that fix 
the CVE. We collect all this data in https://docs.google.com/spreadsheets/d/1qztIwB8xJ10H-2HLX15vI29Ze7yFDOrv7kDQ4JUi1g8/edit?usp=sharing .

We download the package source for each CVE by following the below steps.

1. After finding the Debian package, visit the Debian snapshot site (https://snapshot.debian.org/). On the left sidebar, under the "Packages" section, select "Source Packages" and enter only the source name of the package (for example, for the package `tigervnc_1.7.0-2`, just type `tigervnc`). This will display all available versions of the package. Select the desired version, such as `1.7.0-2` in this case. Since we need to build both the vulnerable and patched versions, and compile binaries with different optimization levels, we will need to download the source files for this purpose.Under source files section, right click on ```package_version.dsc``` and copy the link address. We also provide you an autmated script to find this source link. 


2. **The one important step is to find the right debian version to setup environment**. We provide this step automatically. Having a right debian version is neccessary to guarantee  the installation of debian dependencies. 

3. You can also install and setup enviroment manually. You can install it using virtual machines but we prefer to install it using ```debootstrap```. debootstrap is a tool used to create a minimal Debian-based (or Ubuntu-based) system installation within a directory. It is typically used to bootstrap a new Debian system by downloading essential packages, installing them, and setting up the directory structure needed for a basic system. Follow the following commands. First install deboostrap. 

```bash
sudo apt-get update
sudo apt-get install debootstrap
sudo mkdir /mnt/debian # make a directory to install the debian inside it.
```

Now install the debian using debootstrap. Imagine that we want to install debian 10 or (buster) in directory /mnt/debian10. 

```bash
sudo debootstrap --arch amd64 buster /mnt/debian http://deb.debian.org/debian
sudo chroot /mnt/debian

```

chroot changes the apparent root directory for a process, isolating it from the rest of the system by making it operate within a specified directory as if it were the root (/).

4. You are now inside the debian you just installed. It is now time to install the debian package. Run the following commands. 

```
apt-get update
apt-get install -y --force-yes build-essential fakeroot devscripts packaging-dev
```
Now make a directory for the vulnerable version of the package. 

```
mkdir vulnerable
cd vulnerable
```

Now download the source file you just obtained from the first step. Run the following command.

```
dget -u --insecure source_file_url
```

As an example, it can be like ```dget -u --insecure https://snapshot.debian.org/archive/debian-debug/20161230T030620Z/pool/main/t/tigervnc/tigervnc_1.7.0-2.dsc```.

Now you have downloaded the package in directory vulnerable. **Inside every debian package, there is a directory called /debian/patches/. This directory contains all patches applied into this package. As an example for ```tigervnc_1.10.1%2Bdfsg-4```, you can see this list of patches. 


<img src="images/tigervnc.png"  width="1000"/>

If you open the series file, you will see the list of patches. The Debian community provides an awesome tool named ```quilt``` to apply or remove patches from source code. Quilt uses a file called series to track the list of patches and their order. The patches are applied one after another in the order they are listed in the ```debian/patches/series``` file. The command ```quilt push``` will apply the patch and ```quilt pop``` will remove the patch. In order to find out the applied patches run 

```
quilt applied
```

To know more about quilt please refer to https://raphaelhertzog.com/2012/08/08/how-to-use-quilt-to-manage-patches-in-debian-packages/.

Then you can remove the patch that fix the CVE by using the following command.

```
quilt pop CVE-2014-8240-849479.patch
```
You can also revert all patches by using 

```
quilt pop -a
```

Now it is time to build package dependencies. Thanks to debian community, you can build all dependencies by using following command.It will use debian/rules to build the package.

```
apt build-dep .
```
It is neccessary that this phase should be successfully done.  

You can now install the package for different optimization levels. We build the packages with debug information(dwarf).

```
#optimization level 0
yes '' | DEB_BUILD_OPTIONS='nostrip noopt debug' dpkg-buildpackage -b -uc -us
```

```
#optimization level 1
export CFLAGS="-O1"
export CXXFLAGS="-O1"
export FFLAGS="-O1"
export DEB_BUILD_OPTIONS="nostrip debug"
dpkg-buildpackage -b -uc -us
```
```
#optimization level 2
export CFLAGS="-O2"
export CXXFLAGS="-O2"
export FFLAGS="-O2"
export DEB_BUILD_OPTIONS="nostrip debug"
dpkg-buildpackage -b -uc -us
```

```
#optimization level 3
export CFLAGS="-O3"
export CXXFLAGS="-O3"
export FFLAGS="-O3"
export DEB_BUILD_OPTIONS="nostrip debug"
dpkg-buildpackage -b -uc -us
```

For patch version, just apply the patch using following command. 

```
quilt push file.patch
```
to apply all patches run. 

```
quilt push -a
```
and then build dependencies and the package using above commands. If this step goes through successfully, then the deb files are created. 



## Automation

We automated all the above steps in binpool_automation. 

for more details and understand how to run the automation proccess, we refer the reader to https://github.com/GiorgosNikitopoulos/binpool_automation/tree/0c335d8d1b635305696e01a56f098e37f8cd34b6


## Usage 

After downaloding our dataset, run extract_deb_tar.py to extract debian files into binaries. you should see this structure. 

```
CVE-ID/
│
├── vulnerable/                
│   ├── opt0/                  
│   │   └── debfiles/          # Extracted Debian package files
│   │       └── bins/          # Extracted binaries
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
└── patch/                     # Directory containing patched versions
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

All BinPool statistics is collected in .

to extract the statistics you can run the following command. 

```
python3 extract_statistics.py
```

## Team

### Sima Arasteh
**PhD Student/ University of Southern California**  

### Georgios Nikitopoulos
**PhD Student / Dartmouth College**  

### Wei-Cheng Wu
**PhD Student / Dartmouth College**  

### Nicolaas Weideman
**PhD Student / USC ISI** 

### Aaron Portnoy
**Hacker-in-Residence/ Dartmouth College** 
 
### Mukund Raghothaman
**Assistant Professor / University of Southern California**  

### Christophe Hauser
**Assistant Professor / Dartmouth College**  

