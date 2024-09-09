# BinPool

<p align="center">
<img src="images/binpool.png" alt="Project Logo" width="300"/>
</p>

## Table of Contents
- [Introduction](#introduction)
- [Access](#Access)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Introduction

BinPool is a dataset consisting of vulnerable and patched binaries derived from historical Debian packages. BinPool can be used for vulnerability discovery tasks through various methods, including machine learning, fuzzing, and more. BinPool contains #number of binaries and #number of functions. It covers # of different CWE types. BinPool provides different features as follows.
You can find the BinPool paper in . 

## Access
You can download the dataset from . 

## Features

- It Provides # number of unique CVEs and the corresponding CWE.
- For each CVE, it provides the fix version of the debian package. 
- It provides the primary programming language (C, C++, java, python)
- It provides function names exits in the patch and corresponding line numbers.

## Installation

If you want to build BinPool, follow these steps. 

We built BinPool by integrating debian snapshot , NVD and debian security tracker. You can access the link of binpool
records from https://docs.google.com/spreadsheets/d/1qztIwB8xJ10H-2HLX15vI29Ze7yFDOrv7kDQ4JUi1g8/edit?usp=sharing. 

For each CVE in the link above, grab the corresponding fix version. This is the version of the package that fix this CVE. For each CVE, there are more than one fix version but you can try to grab anyone. Note that usually if the version is higher, it is more likely to get built. 

1. After finding the Debian package, visit the Debian snapshot site (https://snapshot.debian.org/). On the left sidebar, under the "Packages" section, select "Source Packages" and enter only the source name of the package (for example, for the package `tigervnc_1.7.0-2`, just type `tigervnc`). This will display all available versions of the package. Select the desired version, such as `1.7.0-2` in this case.On the version page, you will find both the source files and binary packages. Thanks to the Debian community, all source packages are pre-built and available for download. The binaries contain only patched functions. Since we need to build both the vulnerable and patched versions, and compile binaries with different optimization levels, we will need to download the source files for this purpose.Under source files section, right click on ```package_version.dsc``` and copy the link address. We also provide you an autmated script to find this source link. 


2. **The most important and challenging part of debian packages is to find the right debian version to build the debian package inside.** We provide an automated script to find a right debian version for each package. 

3. 
